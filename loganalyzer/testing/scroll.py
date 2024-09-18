def cursor1(self):
    self.vLines = {}
    self.vb_dict = {}

    for plot_name, plot_item in self.plotDict.items():
        if plot_name == 'vtime' or plot_name == 'mainPlot':
            continue

        # Add vertical line to each plot
        vLine = pg.InfiniteLine(angle=90, movable=False)
        plot_item.addItem(vLine, ignoreBounds=True)
        self.vLines[plot_name] = vLine

        # Store reference to the view box
        self.vb_dict[plot_name] = plot_item.vb

        # Connect mouse movement signal to the handler
        plot_item.scene().sigMouseMoved.connect(self.create_mouseMoved_handler(plot_name))


def create_mouseMoved_handler(self, plot_name):
    return lambda evt: self.mouseMoved1(evt, plot_name)


def mouseMoved1(self, evt, plot_name):
    pos = evt
    plot_item = self.plotDict[plot_name]

    if plot_item.sceneBoundingRect().contains(pos):
        mousePoint = self.vb_dict[plot_name].mapSceneToView(pos)
        index = int(mousePoint.x())
        new_index = min(self.lists_dict["vtime"], key=lambda x: abs(x - index))
        x = self.lists_dict["vtime"].index(new_index)

        self.values = []  # Reset values for updated display
        for a in self.plotDict:
            if a == 'vtime' or a == 'mainPlot':
                continue

            a_value = self.lists_dict[a][x]
            found = False
            for parameter in self.values:
                if parameter[0] == a:
                    parameter[1] = a_value
                    found = True
                    break
            if not found:
                self.values.append([a, a_value])

        formatted_text = "<span style='font-size: 12pt'>vtime=%0.1f ms" % (mousePoint.x())
        formatted_text += "<br>" + "<br>".join([f"{a}: {value}" for a, value in self.values])
        self.label_text2.setHtml(formatted_text)

        # Update vertical line position for all plots
        for vLine in self.vLines.values():
            vLine.setPos(mousePoint.x())






    def cursor1(self):
        vLine = pg.InfiniteLine(angle=90, movable=False)  # Single vertical line
        self.vb_dict = {}  # Store references to the view boxes

        for plot_name, plot_item in self.plotDict.items():
            if plot_name == 'vtime' or plot_name == 'mainPlot':
                continue

            self.add_cursor_to_plot(plot_name)
