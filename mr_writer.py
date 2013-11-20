#!/usr/bin/env python

# MrWriter - Trivial image writer tool
#
# Copyright (C) 2013 Nick Glynn <Nick.Glynn@feabhas.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA

import os
import gtk
import gobject
import threading
import subprocess

global IMAGE_DIRECTORY


class ImageWriter(gtk.Dialog):
    def __init__(self, parent, image, drives):
        gtk.Dialog.__init__(self, self.__class__.__name__, parent,
                            0,
                            (gtk.STOCK_CLOSE, gtk.RESPONSE_NONE))
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        self.connect("response", lambda d, r: d.destroy())

        self.set_resizable(False)
        self.still_working = False

        self.set_modal(True)
        self.set_size_request(300, 180)

        self.finished = True
        # Tell WM this is a dialog
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        # Tell WM this window belongs to parent
        self.set_transient_for(parent)

        vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(vbox, True, True, 0)
        vbox.set_border_width(5)

        self.label = gtk.Label()
        self.label_text = "Wait for it..."
        self.label.set_line_wrap(True)
        vbox.pack_start(self.label, False, False, 0)

        # Create our entry
        self.progress = gtk.ProgressBar()
        vbox.pack_start(self.progress, False, False, 0)

        self.drive_list = drives
        self.image_file = image

        gobject.timeout_add(400, self.pulse)
        t = threading.Thread(target=self.write_thread)
        t.setDaemon(True)
        t.start()
        self.show_all()
        self.run()

    def pulse(self):
        self.progress.pulse()
        gtk.gdk.threads_enter()
        self.label.set_text(self.label_text)
        gtk.gdk.threads_leave()
        if self.finished:
            self.progress.set_fraction(1.0)
            self.label_text = "Finished!"
            self.label.set_text(self.label_text)
            return False
        return True

    def write_thread(self):
        self.finished = False
        for drive in self.drive_list:
            self.label_text = "Writing %s to drive %s" % (
                self.image_file, drive)

            # The actual write process
            command = ["dd", "if=" + IMAGE_DIRECTORY +
                       self.image_file, "of=" + drive, "bs=8M"]
            print command
            sp = subprocess.Popen(command, shell=False,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

            self.stdout, self.stderr = sp.communicate()
            print self.stdout
            print self.stderr
        self.finished = True


class MrWriter(gtk.Window):
    drive_list = []

    def __init__(self):
        gtk.Window.__init__(self)
        self.image_list = self.get_image_list()
        self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title("USB Image Writer")
        self.set_size_request(320, 160)
        self.set_position(gtk.WIN_POS_CENTER)
        vbox = gtk.VBox(spacing=10)
        vbox.set_border_width(10)

        top_box = gtk.HBox(spacing=10)
        top_box.pack_start(gtk.Label("Select Image:"), expand=False)
        top_box.pack_start(self.image_list, expand=True)
        vbox.pack_start(top_box, expand=False)

        mid_box = gtk.HBox(spacing=10)
        mid_box.set_border_width(10)
        self.drive_label = gtk.Label(
            "Ready to write to %d drives" % self.get_drive_count())
        image = gtk.Image()
        #  (from http://www.pygtk.org/docs/pygtk/gtk-stock-items.html)
        image.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
        update_button = gtk.Button()
        update_button.set_image(image)
        update_button.set_label("")
        update_button.get_image().show()
        update_button.connect("clicked", self.on_update_drive_count)
        mid_box.pack_start(self.drive_label, expand=True)
        mid_box.pack_start(update_button, expand=False)
        vbox.pack_start(mid_box, expand=False)

        # TODO: Confirmation button
        self.go_box = gtk.Table(1, 2, True)
        write_image_button = gtk.Button("Write Images")
        write_image_button.connect("clicked", self.on_write_image_clicked)
        self.go_box.attach(write_image_button, 1, 2, 0, 1)
        vbox.pack_start(self.go_box, expand=False)

        self.add(vbox)

        #vbox.pack
        self.show_all()

    def on_update_drive_count(self, data):
        print "Any more drives"
        self.drive_label.set_text(
            "Ready to write to %d drives" % self.get_drive_count())
        self.show_all()

    def on_write_image_clicked(self, data):
        # Get the image selected

        image_writer = ImageWriter(
            self, self.image_list.get_active_text(), self.drive_list)

    def get_drive_count(self):
        self.drive_list = []

        # Find our mounts in /run/mount/utab
        f = open("/run/mount/utab").readlines()

        for drive in os.listdir("/dev/"):
            if drive.startswith("sd") and drive.isalpha():
                for line in f:
                    if drive in line:
                        self.drive_list.append("/dev/" + drive)

        print "Found %d drives" % len(self.drive_list)
        return len(self.drive_list)

    def get_image_list(self):
        image_list = gtk.combo_box_new_text()
        for image in os.listdir(IMAGE_DIRECTORY):
            if image.endswith(".img"):
                image_list.append_text(image)
            image_list.set_active(0)
        # TODO: Check and error if there are no images
        return image_list


if __name__ == "__main__":
    print "Running with eUID ", os.geteuid()
    gtk.gdk.threads_init()
    # Try and read the images directory
    import ConfigParser as cp
    try:
        config = cp.ConfigParser()
        tempConfig = config.read("./mr_writer.ini")
        IMAGE_DIRECTORY = config.get("General", "ImageDir")
        print IMAGE_DIRECTORY
        if not os.path.isdir(IMAGE_DIRECTORY):
            raise NameError('Invalid Directory')

        app = MrWriter()
        app.show()
        gtk.main()
    except:
        message = gtk.MessageDialog(
            type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup(
            "You need to set a valid image directory in mr_writer.ini")
        message.run()
