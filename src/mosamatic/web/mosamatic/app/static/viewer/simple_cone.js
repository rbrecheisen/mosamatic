console.log(document.currentScript.dataset.datasetName);

const container = document.querySelector("#container");
const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
const renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
renderWindow.addRenderer(renderer);

const openGLRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
openGLRenderWindow.setContainer(container);
openGLRenderWindow.setSize(512, 512);
renderWindow.addView(openGLRenderWindow);

const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
interactor.setView(openGLRenderWindow);
interactor.initialize();
interactor.bindEvents(container);

const trackball = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
interactor.setInteractorStyle(trackball);

const cone = vtk.Filters.Sources.vtkConeSource.newInstance();
const actor = vtk.Rendering.Core.vtkActor.newInstance();
const mapper = vtk.Rendering.Core.vtkMapper.newInstance();

actor.setMapper(mapper);
mapper.setInputConnection(cone.getOutputPort());
renderer.addActor(actor);

renderer.resetCamera();
renderWindow.render();
