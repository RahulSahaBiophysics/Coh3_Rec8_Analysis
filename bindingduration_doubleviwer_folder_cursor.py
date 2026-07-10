import napari
import tifffile
import os
import numpy as np
import pandas as pd
from qtpy.QtWidgets import QPushButton, QFileDialog, QSlider, QLabel, QVBoxLayout, QWidget
from qtpy.QtCore import Qt


#This script open image and kymo in separate napari viewer and multiple images can be opened one by one
# APP STATE
# =========================================================
class AppState:
    def __init__(self):
        self.file_list = []
        self.index = 0

        self.filename = None
        self.ch1 = None
        self.ch2 = None

        self.kymo1 = None
        self.kymo2 = None

state = AppState()


# -------------------------
# VIEWERS
# -------------------------
image_viewer = napari.Viewer(title="Images")
kymo_viewer = napari.Viewer(title="Kymographs")

# =========================================================
# UI: filename display
# =========================================================
file_label = QLabel("No file loaded")
kymo_viewer.window.add_dock_widget(file_label, area="top")

def update_label():
    if state.filename:
        file_label.setText(
            f"{state.index+1}/{len(state.file_list)} → "
            f"{os.path.basename(state.filename)}"
        )

# -------------------------
# STATE
# -------------------------
"""file_list = []
file_index = 0

ch1 = None
ch2 = None

kymo1 = None
kymo2 = None"""




# -------------------------
# LOAD FOLDER
# -------------------------
def load_folder(event=None):
    #global file_list, file_index

    folder = QFileDialog.getExistingDirectory(None, "Select folder")

    if not folder:
        return

    state.file_list = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith("_processed.tif") or f.endswith("_processed.tiff")
    ])

    state.index = 0
    load_file()


# -------------------------
# LOAD SINGLE FILE
# -------------------------
def load_file():

    if not state.file_list:
        return


    path = state.file_list[state.index]
    state.filename = path

    img = tifffile.imread(path)

    state.ch1 = img[:, 0]
    state.ch2 = img[:, 1]

    #print(f"Loaded {file_index+1}/{len(file_list)}:", os.path.basename(path))

    # update viewer
    if "Ch1" in image_viewer.layers:
        image_viewer.layers["Ch1"].data = state.ch1
        image_viewer.layers["Ch2"].data = state.ch2
    else:
        image_viewer.add_image(state.ch1, name="Ch1", colormap="red",blending="additive")
        image_viewer.add_image(state.ch2, name="Ch2", colormap="cyan",blending="additive")

    update_label()
    print("Loaded:", path)

# -------------------------
# NEXT / PREV FILES
# -------------------------
def next_file():
    if state.index < len(state.file_list) - 1:
        state.index += 1
        load_file()

def prev_file():
    if state.index > 0:
        state.index -= 1
        load_file()

# =========================================================
# ROI (IMAGE SPACE)
# =========================================================
roi_layer = image_viewer.add_shapes(
    name="ROI",
    shape_type="rectangle",
    edge_color="yellow",
    face_color=[1, 1, 0, 0],
    blending="additive"
)




# -------------------------
# KYMOGRAPH
# -------------------------
kymo_layer_ch1 = None
kymo_layer_ch2 = None


# =========================================================
# FRAME SLIDER + CURSOR
# =========================================================
frame_slider = QSlider(Qt.Horizontal)
frame_label = QLabel("Frame: 0")

kymo_cursor = kymo_viewer.add_shapes(
    name="Frame Cursor",
    shape_type="line",
    edge_color="white",
    edge_width=2
)



def update_cursor(v):
    if state.kymo1 is None:
        return

    w = state.kymo1.shape[1]  # spatial axis (width)

    # vertical line at frame v
    line = np.array([
        [0, v],
        [w, v]
    ])

    kymo_cursor.data = [line]

def on_frame_change(v):
    frame_label.setText(f"Frame: {v}")

    if kymo_layer_ch1 is not None:
        kymo_layer_ch1.current_step = (v,)
        kymo_layer_ch2.current_step = (v,)

    update_cursor(v)   



frame_slider.valueChanged.connect(on_frame_change)

frame_widget = QWidget()
layout = QVBoxLayout()
layout.addWidget(frame_label)
layout.addWidget(frame_slider)
frame_widget.setLayout(layout)

kymo_viewer.window.add_dock_widget(frame_widget, area="bottom")

def generate_kymo():
    

    if state.ch1 is None:
        print("Load image first")
        return
    
    if len(roi_layer.data) == 0:
        print("Draw ROI first")
        return

    roi = roi_layer.data[0]

    ymin, ymax = int(np.min(roi[:, 0])), int(np.max(roi[:, 0]))
    xmin, xmax = int(np.min(roi[:, 1])), int(np.max(roi[:, 1]))

    p1, p2 = [], []

    for f1, f2 in zip(state.ch1, state.ch2):
        c1 = f1[ymin:ymax, xmin:xmax]
        c2 = f2[ymin:ymax, xmin:xmax]

        p1.append(c1.mean(axis=0))
        p2.append(c2.mean(axis=0))

    state.kymo1 = np.stack(p1).T
    state.kymo2 = np.stack(p2).T

    print("kymo1 shape:", state.kymo1.shape)

    global kymo_layer_ch1, kymo_layer_ch2

    if kymo_layer_ch1 is None:
        kymo_layer_ch1 = kymo_viewer.add_image(state.kymo1, name="Kymo Ch1", colormap="red",blending="additive")
        kymo_layer_ch2 = kymo_viewer.add_image(state.kymo2, name="Kymo Ch2", colormap="cyan",blending="additive")
    else:
        kymo_layer_ch1.data = state.kymo1
        kymo_layer_ch2.data = state.kymo2

    # set slider range
    frame_slider.setMaximum(state.kymo1.shape[1] - 1)
    frame_slider.setValue(0)

    update_cursor(0)

    print("Kymograph ready")

# ROI on kymograph
# -------------------------
kymo_roi = kymo_viewer.add_shapes(
    name="Protein binding ROIs",
    shape_type="rectangle",
    edge_color="yellow",
    edge_width=2,
    face_color=[1, 1, 0, 0],
    blending="additive"
)

# =========================================================
# SAVE RESULTS
# =========================================================
def save_results():
    if state.filename is None:
        return

    results = []

    for i, roi in enumerate(kymo_roi.data):
        y = roi[:, 1]
        start, end = int(np.min(y)), int(np.max(y))

        frames = end - start + 1
        duration = frames * 0.2

        results.append({
            "ROI": i+1,
            "Start": start, 
            "End": end,
            "Length (frames)": frames,
            "Duration (s)": duration})


    df = pd.DataFrame(results)

    out_folder = os.path.dirname(state.filename)
    base = os.path.splitext(os.path.basename(state.filename))[0]

    out_file = os.path.join(out_folder, f"{base}_events.csv")

    df.to_csv(out_file, index=False)
    print("Saved:", out_file)

# -------------------------
# UI BUTTONS
# -------------------------
btn_folder = QPushButton("Load Folder")
btn_folder.clicked.connect(load_folder)
image_viewer.window.add_dock_widget(btn_folder, area="right")

btn_prev = QPushButton("Previous File")
btn_prev.clicked.connect(prev_file)
image_viewer.window.add_dock_widget(btn_prev, area="right")

btn_next = QPushButton("Next File")
btn_next.clicked.connect(next_file)
image_viewer.window.add_dock_widget(btn_next, area="right")

btn_kymo = QPushButton("Generate Kymo")
btn_kymo.clicked.connect(generate_kymo)
image_viewer.window.add_dock_widget(btn_kymo, area="right")

btn_save = QPushButton("Save Events")
btn_save.clicked.connect(save_results)
kymo_viewer.window.add_dock_widget(btn_save, area="right")



napari.run()