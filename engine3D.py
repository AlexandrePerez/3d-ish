# Alexandre Perez, 2018
# Graphic engine based only on Tkinter.
#
# It can only render writeframes objects as if an observer was looking through a window.
# Assumptions:
# 1. In an direct orthographic base, the window is in the (XY) plan.
# 2. The observer (followed by the window) can move but can not rotate.
# See the drawing below.
#
# Obs  Window    Shape
#     Y|\X
#      | \
#      |  \   Z
#   O   \s-|----->S
#        \ |
#         \|
#
import tkinter as tk


class Engine:
    """Simple graphic engine."""
    def __init__(self, root=None, canvas=None, obs=None, window_pos=None, window_size=None):
        # Tk
        self.root = root
        # Canvas
        self.canvas = canvas
        # Width, height of the canvas
        self.canvas_shape = [0, 0]

        # Observer coordinate (focal)
        if obs:
            self.obs = obs
        else:
            self.obs = [0.0, 0.0, -1.0]
        # Window coordinate (top-left)
        if window_pos:
            self.window_pos = window_pos
        else:
            self.window_pos = [-0.5, -0.5, 0.0]
        # Window width and length
        if window_size:
            self.window_size = window_size
        else:
            self.window_size = [1.0, 1.0]
        # Shapes in the scene
        self.shapes = []
        # id of the lines
        self.canvas_id = []

    def init(self, root=None, canvas=None):
        """Initialize the canvas"""
        if canvas:
            self.canvas = canvas
        if root:
            self.tk = root
        self.canvas.configure(background='#ffffff')
        self.canvas.pack(expand=True, fill="both")
        self.draw()

    def move_obs(self, vect):
        """Translate the observer"""
        for i, x in enumerate(vect):
            self.obs[i] += x
            self.window_pos[i] += x

    def add_shape(self, shape):
        """Add a Shape to draw"""
        self.shapes.append(shape)

    def render(self):
        """Compute the new rendering"""
        for s in self.shapes:
            s.window_projection(self.obs, self.window_pos)

    def draw(self):
        """Draw the shapes in the Canvas"""
        # Remove the old shapes
        for cid in self.canvas_id:
            self.canvas.delete(cid)
        self.canvas_id = []

        # Draw new shapes
        for s in self.shapes:
            for edge in s.edges:
                a = s.verts_proj[edge[0]]
                b = s.verts_proj[edge[1]]
                # print("vertices to link:  %s  | %s" % (a, b))

                # TODO convert meter to pixel : find a better multiplication factor (in param)
                mult = 200.0
                # Place the center of the canvas at the center of the window
                translation_x = float(self.canvas_shape[0]) / 2
                translation_y = float(self.canvas_shape[1]) / 2

                self.canvas_id.append(self.canvas.create_line(a[0]*mult+translation_x, a[1]*mult+translation_y,
                                      b[0]*mult+translation_x, b[1]*mult+translation_y))

    def update(self, func=None):
        """Update the scene every 30ms.
        Elements of the scene can be changed by giving an (optional) function as argument.
        E.g. engine.update(update_in_other_module) OR root.after(timer, self.update, update_in_other_module)
        """
        if func:
            func()

        self.canvas_shape = [self.canvas.winfo_width(), self.canvas.winfo_height()]

        self.render()
        # print("Z_obs = %0.02f" % self.obs[2])
        # print(self.shapes[0].verts[0])
        # print(self.shapes[0].verts_proj[0])

        self.draw()
        self.root.after(30, self.update, func)


class Shape:
    """A Shape is defined by its vertices and edges."""
    def __init__(self, verts=None, edges=None):
        # Points
        if verts is None:
            self.verts = []
        else:
            self.verts = verts
        # Edges
        if edges is None:
            self.edges = []
        else:
            self.edges = edges
        # Vertices projected in the window plane
        self.verts_proj = []

    def window_projection(self, obs, window_pos):
        """Project the points on the window plane (XY) with respect to the observer"""
        self.verts_proj = []
        for p in self.verts:
            p2 = [0.0, 0.0]
            if p[0] != obs[0]:
                a0 = (p[2] - obs[2]) / (p[0] - obs[0])
                p2[0] = (1/a0) * (window_pos[2] - obs[2] + a0 * obs[0])
            else:
                p2[0] = p[0]

            if p[1] != obs[1]:
                a1 = (p[2] - obs[2]) / (p[1] - obs[1])
                p2[1] = (1 / a1) * (window_pos[2] - obs[2] + a1 * obs[1])
            else:
                p2[1] = p[1]
            self.verts_proj.append(p2)


class Square(Shape):
    def __init__(self, pos=None, size=1):
        """Create a Square shape, default is a centered 1*1*1 square."""
        v = [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]
        e = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]]

        size = float(size) / 2
        if pos is None:
            pos = [0.0, 0.0, 0.0]
        for i in range(len(v)):
            v[i][0] = v[i][0]*size + pos[0]
            v[i][1] = v[i][1] * size + pos[1]
            v[i][2] = v[i][2] * size + pos[2]

        Shape.__init__(self, verts=v, edges=e)


if __name__ == "__main__":
    print("Example\n=======")

    # Instantiate the window
    print("Initializing the window...")
    root = tk.Tk()
    root.title("Test 3D")
    root.geometry("600x500")
    # The canvas to draw
    canvas = tk.Canvas(root)

    # Initialize engine
    print("Initializing the engine...")
    # The obeserver is 1m behind a centered 1*1m window
    eng = Engine(root=root, canvas=canvas, obs=[0.0, 0.0, -1.0], window_pos=[-0.5, -0.5, 0.0], window_size=[1.0, 1.0])
    eng.init()

    # Instantiate a grid of cubes
    print("Initializing the scene...")
    for i in range(-2, 3):
        for j in range(-2, 3):
            eng.add_shape(Square(pos=[1.1*i, 1.1*j, 4], size=1))
    eng.render()

    #
    def updater():
        """Go back, then go dawn, then go right"""
        if eng.obs[2] > -2:
            eng.move_obs([0.0, 0.00, -0.05])
        elif eng.obs[1] < 1:
            eng.move_obs([0.00, 0.05, 0.00])
        elif eng.obs[0] < 1:
            eng.move_obs([0.05, 0.0, 0.00])

    # Start the demo
    print("Starting the animation...")
    root.after(1000, eng.update, updater)
    root.mainloop()
