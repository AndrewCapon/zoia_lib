import json
import os
from os.path import expanduser
from threading import Thread

from PyQt5.uic.properties import QtGui
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import zoia_lib.UI.throwaway as ui_main
import zoia_lib.backend.api as api
import zoia_lib.backend.utilities as util

ps = api.PatchStorage()
backend_path = util.get_backend_path()

style_sheet = """
    QPushButton
    {
        background: white;
        border: none;
        font-size: 14px;
        color: black;
    }
    """


class ThrowawayUIMain(QMainWindow):

    def __init__(self):
        super(ThrowawayUIMain, self).__init__()
        self.ui = ui_main.Ui_MainWindow()
        self.ui.setupUi(self)

        self.data = ps.get_all_patch_data_min()["patch_list"]
        self.search_data = None
        self.sd_card_path = None
        self.local_data = None
        self.search_local_data = None

        self.create_table()

        self.ui.left_widget.currentChanged.connect(self.get_local_patches)
        self.ui.actionSort_by_title_A_Z.triggered.connect(self.sort)
        self.ui.actionSort_by_title_Z_A.triggered.connect(self.sort)
        self.ui.actionSort_by_date_new_old.triggered.connect(self.sort)
        self.ui.actionSort_by_date_old_new.triggered.connect(self.sort)
        self.ui.actionSort_by_likes_high_low.triggered.connect(self.sort)
        self.ui.actionSort_by_likes_low_high.triggered.connect(self.sort)
        self.ui.actionSort_by_views_high_low.triggered.connect(self.sort)
        self.ui.actionSort_by_views_low_high.triggered.connect(self.sort)
        self.ui.actionSort_by_downloads_high_low.triggered.connect(self.sort)
        self.ui.actionSort_by_downloads_low_high.triggered.connect(self.sort)
        self.ui.actionSpecify_SD_Card_Location.triggered.connect(self.sd_path)
        self.ui.actionQuit.triggered.connect(self.try_quit)
        self.ui.search_button_3.clicked.connect(self.search)

        self.ui.table.setFont(QFont('SansSerif', 11))
        self.ui.right_widget.setFont(QFont('SansSerif', 16))

        self.showMaximized()

    def create_table(self):
        self.ui.table.setRowCount(len(self.data))
        self.ui.table.setColumnCount(5)
        self.set_data(False)
        self.ui.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.table.resizeColumnsToContents()
        self.ui.table.resizeRowsToContents()

    def get_local_patches(self):
        if self.ui.left_widget.currentIndex() == 1:
            self.ui.right_widget.setText("")
            self.local_data = []
            for patches in os.listdir(backend_path):
                if patches != "Banks":
                    for pch in os.listdir(os.path.join(backend_path, patches)):
                        if pch.split(".")[1] == "json":
                            with open(os.path.join(backend_path,
                                                   patches, pch)) as f:
                                temp = json.loads(f.read())
                            self.local_data.append(temp)
            self.set_data_local(False)
        else:
            self.ui.right_widget.setText("")
            self.set_data(False)


    def set_data(self, search):
        self.ui.table.clear()
        if search:
            data = self.search_data
        else:
            data = self.data
        self.ui.table.setRowCount(len(data))
        hor_headers = ["Title", "Tags", "Categories", "Date Modified", "Download"]
        for i in range(len(data)):
            btn_title = QRadioButton(data[i]["title"], self)
            btn_title.setObjectName(str(data[i]["id"]))
            btn_title.toggled.connect(self.display_patch_info)
            self.ui.table.setCellWidget(i, 0, btn_title)
            tags = ""
            for j in range(1, len(data[i]["tags"])):
                tags += data[i]["tags"][j]["name"] + ", "
            tags = tags[:len(tags) - 2]
            if (len(data[i]["tags"])) > 1:
                btn_tag = QPushButton(data[i]["tags"][0]["name"]
                                      + " and " + str(len(data[i]["tags"])
                                                      - 1) + " more", self)
            else:
                btn_tag = QPushButton(data[i]["tags"][0]["name"], self)
            QToolTip.setFont(QFont('SansSerif', 11))
            btn_tag.setToolTip(tags)
            btn_tag.setStyleSheet(style_sheet)
            btn_tag.setFont(QFont('SansSerif', 11))
            self.ui.table.setCellWidget(i, 1, btn_tag)

            cat = ""
            for k in range(1, len(data[i]["categories"])):
                cat += data[i]["categories"][k]["name"] + ", "
            cat = cat[:len(cat) - 2]
            if (len(data[i]["categories"])) > 1:
                btn_cat = QPushButton(data[i]["categories"][0]["name"]
                                      + " and "
                                      + str(len(data[i]["categories"])
                                            - 1) + " more", self)
            else:
                btn_cat = QPushButton(data[i]["categories"][0]["name"], self)
            QToolTip.setFont(QFont('SansSerif', 11))
            btn_cat.setToolTip(cat)
            btn_cat.setFont(QFont('SansSerif', 11))
            btn_cat.setStyleSheet(style_sheet)
            self.ui.table.setCellWidget(i, 2, btn_cat)
            date = QTableWidgetItem(data[i]["updated_at"][:10])
            date.setTextAlignment(Qt.AlignCenter)
            self.ui.table.setItem(i, 3, date)
            dwn = QPushButton(str(data[i]["id"]), self)
            dwn.setFont(QFont('SansSerif', 11))
            dwn.clicked.connect(self.initiate_download)
            if (str(data[i]["id"])) in os.listdir(backend_path):
                dwn.setEnabled(False)
                dwn.setText("Downloaded!")
            self.ui.table.setCellWidget(i, 4, dwn)
        self.ui.table.setHorizontalHeaderLabels(hor_headers)

    def set_data_local(self, search):
        self.ui.table_2.clear()
        if search:
            data = self.local_search_data
        else:
            data = self.local_data
        self.ui.table.setRowCount(len(data))
        hor_headers = ["Title", "Tags", "Categories", "Date Modified", "Export"]
        for i in range(len(data)):
            btn_title = QRadioButton(data[i]["title"], self)
            btn_title.setObjectName(str(data[i]["id"]))
            btn_title.toggled.connect(self.display_patch_info)
            self.ui.table.setCellWidget(i, 0, btn_title)
            tags = ""
            for j in range(1, len(data[i]["tags"])):
                tags += data[i]["tags"][j]["name"] + ", "
            tags = tags[:len(tags) - 2]
            if (len(data[i]["tags"])) > 1:
                btn_tag = QPushButton(data[i]["tags"][0]["name"]
                                      + " and " + str(len(data[i]["tags"])
                                                      - 1) + " more", self)
            else:
                btn_tag = QPushButton(data[i]["tags"][0]["name"], self)
            QToolTip.setFont(QFont('SansSerif', 11))
            btn_tag.setToolTip(tags)
            btn_tag.setStyleSheet(style_sheet)
            btn_tag.setFont(QFont('SansSerif', 11))
            self.ui.table.setCellWidget(i, 1, btn_tag)

            cat = ""
            for k in range(1, len(data[i]["categories"])):
                cat += data[i]["categories"][k]["name"] + ", "
            cat = cat[:len(cat) - 2]
            if (len(data[i]["categories"])) > 1:
                btn_cat = QPushButton(data[i]["categories"][0]["name"]
                                      + " and "
                                      + str(len(data[i]["categories"])
                                            - 1) + " more", self)
            else:
                btn_cat = QPushButton(data[i]["categories"][0]["name"], self)
            QToolTip.setFont(QFont('SansSerif', 11))
            btn_cat.setToolTip(cat)
            btn_cat.setFont(QFont('SansSerif', 11))
            btn_cat.setStyleSheet(style_sheet)
            self.ui.table.setCellWidget(i, 2, btn_cat)
            date = QTableWidgetItem(data[i]["updated_at"][:10])
            date.setTextAlignment(Qt.AlignCenter)
            self.ui.table.setItem(i, 3, date)
            expt = QPushButton(str(data[i]["id"]), self)
            expt.setFont(QFont('SansSerif', 11))
            expt.clicked.connect(self.initiate_export)
            self.ui.table.setCellWidget(i, 4, expt)
        self.ui.table.setHorizontalHeaderLabels(hor_headers)

    def initiate_download(self):
        self.ui.statusbar.showMessage("Starting download...")
        idx = str(self.sender().text())
        self.sender().setText("...")
        self.sender().show()
        thread = Thread(target=self.download_and_save, args=(idx, self.sender(),))
        thread.start()
        # TODO Replace with FCFS scheduling
        thread.join()

    def initiate_export(self):
        if self.sd_card_path is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Please specify your SD card path!")
        else:
            util.export_patch_bin(self.sender().text(), self.sd_card_path, 8)
        self.ui.statusbar.showMessage("Starting download...")
        idx = str(self.sender().text())
        self.sender().setText("...")
        self.sender().show()
        thread = Thread(target=self.download_and_save, args=(idx, self.sender(),))
        thread.start()
        # TODO Replace with FCFS scheduling
        thread.join()

    def download_and_save(self, idx, btn):
        data = ps.download(idx)
        util.save_to_backend(data)
        btn.setEnabled(False)
        btn.setText("Downloaded!")
        self.ui.statusbar.showMessage("Download complete!", timeout=2)

    def display_patch_info(self):
        btn = self.sender()
        if btn.isChecked():
            content = ps.get_patch_meta(btn.objectName())
            if content["preview_url"] == "":
                content["preview_url"] = "None provided"
            content["content"] = content["content"].replace("\n", "<br/>")
            self.ui.right_widget.setText("<html><h3>"
                                         + content["title"]
                                         + "</h3><u>Author:</u> "
                                         + content["author"]["name"]
                                         + "<br/><u>Likes:</u> "
                                         + str(content["like_count"])
                                         + "<br/><u>Downloads:</u> "
                                         + str(content["download_count"])
                                         + "<br/><u>Views:</u> "
                                         + str(content["view_count"])
                                         + "<br/><u>Preview:</u> "
                                         + content["preview_url"]
                                         + "<br/><br/><u>Patch Notes:</u><br/>"
                                         + content["content"]
                                         + "</html>")

    def sd_path(self):
        input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                     expanduser("~"))
        self.ui.sd_card_path = str(input_dir)

    def search(self):
        if self.ui.searchbar_3.text() == "":
            self.set_data(False)
        else:
            self.search_data = \
                util.search_patches(self.data, self.ui.searchbar_3.text())
            self.set_data(True)

    def sort(self):
        if self.sender().objectName() == "actionSort_by_title_A_Z":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(1, self.data, False)
                self.set_data(False)
            else:
                util.sort_metadata(1, self.search_data, False)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_title_Z_A":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(1, self.data, True)
                self.set_data(False)
            else:
                util.sort_metadata(1, self.search_data, True)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_date_new_old":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(6, self.data, True)
                self.set_data(False)
            else:
                util.sort_metadata(6, self.search_data, True)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_date_old_new":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(6, self.data, False)
                self.set_data(False)
            else:
                util.sort_metadata(6, self.search_data, False)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_likes_high_low":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(3, self.data, True)
                self.set_data(False)
            else:
                util.sort_metadata(3, self.search_data, True)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_likes_low_high":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(3, self.data, False)
                self.set_data(False)
            else:
                util.sort_metadata(3, self.search_data, False)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_views_high_low":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(4, self.data, True)
                self.set_data(False)
            else:
                util.sort_metadata(4, self.search_data, True)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_views_low_high":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(4, self.data, False)
                self.set_data(False)
            else:
                util.sort_metadata(4, self.search_data, False)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_downloads_high_low":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(5, self.data, True)
                self.set_data(False)
            else:
                util.sort_metadata(5, self.search_data, True)
                self.set_data(True)
        elif self.sender().objectName() == "actionSort_by_downloads_low_high":
            if self.ui.searchbar_3.text() == "":
                util.sort_metadata(5, self.data, False)
                self.set_data(False)
            else:
                util.sort_metadata(5, self.search_data, False)
                self.set_data(True)
        else:
            print("How did this even happen?")
            print(self.sender().objectName())

    def try_quit(self):
        self.close()
