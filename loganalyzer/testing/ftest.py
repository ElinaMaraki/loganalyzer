
  def cursor(self):
        for plot_name, plot_item in self.plotDict.items():
            if plot_name == 'vtime' or plot_name == 'mainPlot':
                continue
            vLine = pg.InfiniteLine(angle=90, movable=False)
            plot_item.addItem(vLine, ignoreBounds=True)

            vb = plot_item.vb

        def mouseMoved(evt):
            pos = evt
            if plot_item.sceneBoundingRect().contains(pos):
                mousePoint = vb.mapSceneToView(pos)
                index = int(mousePoint.x())
                new_index = min(self.lists_dict["vtime"], key=lambda x: abs(x - index))
                x = self.lists_dict["vtime"].index(new_index)
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
                vLine.setPos(mousePoint.x())

        self.mouseMovedConnection = plot_item.scene().sigMouseMoved.connect(mouseMoved)
