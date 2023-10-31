import os
import numpy as np
import scipy as sp
import igl
import json
from os.path import basename, splitext


import fast_cd_pyb as fcd
import fast_cody as fc


'''
Runs a standard interactive fast CD simulation, where the user can manipulate a single affine 
handle with a Guizmo and observe secondary effects in real-time.

   
Optional:
    msh_file: path to Tet mesh .msh file (usually generated by TetWild)

    Ws - n x m skinning weights used for simulation. If None, recomputed on the fly
    l - T x 1  per-tet cluster indices. if None, recomputed on the fly. 
    num_modes - if Ws is None, number of skinning modes to compute
    num_clusters - if l is None, number of skinning clusters to compute.
    constraint_enforcements - {"project", "optimal"}. 
                                if "optimal", performs the full constrained GEVP described in the paper. 
                                                This is very slow in python for now, and much faster in Matlab
                                if "project", does an unsconstrained GEVP and projects to the CD constraint set. 
                                default = "project"
    results_dir - directory where results are stored and where cache is stored. if None, then
                    results_dir = "./results/interactive_cd_affine_handle/<msh_file_stem>/
    read_cache - whether to read skinning modes from cache or not (default=False)
    texture_obj - directory pointing towards a .obj file of the surface mesh 
                    containing the UV map required for texture mapping.
                    if None and if texture_png is None, then no texturing is applied. (default=None)
    texture_png - directory pointing towards a .png file of the surface texture.
                  if None and if texture_obj is None, then no texturing is applied. (default=None)      
'''
def interactive_cd_affine_handle(msh_file=None, Ws=None, l=None, mu=1e4, rho=1e3,
                                 num_modes=16, num_clusters=100,
                                 constraint_enforcement="optimal",
                                 results_dir=None, read_cache=False,
                                 texture_png=None, texture_obj=None):
    """
    Runs a standard interactive fast CD simulation, where the user can manipulate a single affine
    handle with a Guizmo and observe secondary effects in real-time.

    Parameters
    ----------
    msh_file : str
        path to Tet mesh .msh file (usually generated by TetWild)
    Ws : (n, m) float numpy array
        n x m skinning weights used for simulation. If None, recomputed on the fly
    l : (t, 1) int numpy array
        T x 1  per-tet cluster indices. if None, recomputed on the fly.
    num_modes : int
        if Ws is None, number of skinning modes to compute
    num_clusters : int
        if l is None, number of skinning clusters to compute.
    constraint_enforcements : str
        {"project", "optimal"}.
        if "optimal", performs the full constrained GEVP described in the paper.
    results_dir : str
        directory where results are stored and where cache is stored. if None, then
    read_cache : bool
        whether to read skinning modes from cache or not (default=False)
    texture_obj : str
        directory pointing towards a .obj file of the surface mesh
        containing the UV map required for texture mapping. If None and if texture_png is None, then no texturing is applied.
    texture_png : str
        directory pointing towards a .png file of the surface texture.
        if None and if texture_obj is None, then no texturing is applied.


    Examples
    --------
    >>> import fast_cody as fcd
    >>> fcd.apps.interactive_cd_affine_handle()
    """
    if msh_file is None:
        msh_file = fc.get_data("./cd_fish.msh")
        if texture_png is None or texture_obj is None:
            texture_png = fc.get_data("./cd_fish_tex.png")
            texture_obj = fc.get_data("./cd_fish_tex.obj")

    assert(splitext(msh_file)[1] == '.msh' and "only supports .msh file format")
    name = basename(splitext(msh_file)[0])
    msh_file = msh_file
    if results_dir is None:
        results_dir = "./results/interactive_cd_affine_handle/" + name + "/"
    cache_dir = results_dir + "/cache/"
    os.makedirs(cache_dir, exist_ok=True)
    [V, F, T] = fcd.readMSH(msh_file)
    [V, so, to] = fcd.scale_and_center_geometry(V, 1, np.array([[0, 0,  0.]])) #center to unit height and about origin

    Wp = np.ones((V.shape[0], 1)) #single handle skinning weight
    J = fc.lbs_jacobian(V, Wp)


    if Ws is None or l is None:
        C = fc.complementary_constraint_matrix(V, T, J, dt=1e-3)
        C2 = fc.lbs_weight_space_constraint(V, C)
        [B, l, Ws] = fc.skinning_subspace(V, T, num_modes, num_clusters, C=C2, read_cache=read_cache,
                                         cache_dir=cache_dir, constraint_enforcement=constraint_enforcement);
    else:
        assert (Ws is not None and l is not None and "Secondary skinning weights and clusters need both be specified")
        num_modes = Ws.shape[1]
        num_clusters = l.max() + 1

    sim = fc.fast_cd_sim(V, T, B, l, J, mu=mu, rho=rho, h=1e-2, cache_dir=cache_dir, read_cache=read_cache)

    # set sim state and initial rig parameters
    z0 = np.zeros((num_modes*12, 1))
    T0 = np.identity(4).astype( dtype=np.float32, order="F");
    p0 = T0[0:3, :].reshape((12, 1))
    st = fc.fast_cd_state(z0, p0)

    step = 0
    def pre_draw_callback():
         nonlocal J, B, T0, sim, st, step
         p = viewer.T0[0:3, :].reshape( (12, 1))
         z = sim.step( p, st)
         st.update(z, p)
         # U = np.reshape(J @ p + B @ z, (J.shape[0]//3, 3), order="F") # full positions
         viewer.update_subspace_coefficients(z, p)
         step += 1

    viewer = fc.viewers.interactive_handle_subspace_viewer(V, T, Wp, Ws,  pre_draw_callback,T0=T0,
                                                  texture_png=texture_png, texture_obj=texture_obj,
                                                  t0=to, s0=so, init_guizmo=True)
    viewer.launch()

