# -*- coding: utf-8 -*-
from __init__ import *

import os
import sys
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QSettings
from src.excel_matches import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('数据一键生成')

        # 初始化 QSettings
        self.settings = QSettings('Basketball', 'DataGenerator')

        # 设置窗口居中
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, 620, 500)

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建文件路径选择区域
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setText('userdata/数据统计.xlsx')
        self.open_file_btn = QPushButton('输入数据')
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.open_file_btn)
        main_layout.addLayout(file_layout)

        # 创建输出路径选择区域
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setText('output')
        self.open_dir_btn = QPushButton('输出目录')
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.open_dir_btn)
        main_layout.addLayout(output_layout)

        # 创建生成按钮
        self.generate_btn = QPushButton('生成')
        main_layout.addWidget(self.generate_btn)

        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        # 创建运行日志区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText('运行日志')
        main_layout.addWidget(self.log_text)

        # 连接信号和槽
        self.open_file_btn.clicked.connect(self.open_file)
        self.open_dir_btn.clicked.connect(self.open_directory)
        self.generate_btn.clicked.connect(self.generate_data)

    def generate_data(self):
        src_path = self.file_path.text()
        output_dir = self.output_path.text()

        if not src_path or not output_dir:
            self.log_text.append('错误：请选择源数据文件和输出目录')
            return

        if not os.path.exists(src_path):
            self.log_text.append('错误：源数据文件不存在')
            return

        if not os.path.exists(output_dir):
            self.log_text.append('错误：输出目录不存在')
            return

        def _update_progress(func=None, val=None, msg="", **kwargs):
            self.log_text.append(msg)
            self.progress_bar.setValue(val)
            if func:
                func(**kwargs)

        try:
            # 使用当前日期生成文件名
            current_date = datetime.now().strftime('%Y%m%d')
            output_path = os.path.join(output_dir, f'赛季数据_{current_date}.xlsx')

            self.progress_bar.setValue(0)
            self.log_text.append('开始处理数据...')
            _update_progress(
                func=generate_match_db,
                val=20,
                msg="正在生成比赛数据库",
                src_path=src_path,
            )
            _update_progress(func=generate_season_db, val=30, msg="正在生成赛季数据库")
            _update_progress(func=generate_avg_db, val=40, msg="正在生成场均数据库")
            _update_progress(func=generate_score_db, val=50, msg="正在生成积分数据库")
            _update_progress(
                func=generate_excel,
                val=60,
                msg="正在生成Excel文件",
                path=output_path,
            )
            _update_progress(
                func=formal_excel,
                val=70,
                msg="正在格式化Excel文件",
                src_path=output_path,
            )

            self.progress_bar.setValue(100)
            self.log_text.append(f'数据处理完成！输出文件：{output_path}')

        except Exception as e:
            self.log_text.append(f'错误：{str(e)}')
            self.progress_bar.setValue(0)

    def open_file(self):
        # 获取上次打开的目录路径
        last_dir = os.path.dirname(self.settings.value('last_file_path', ''))

        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", last_dir, "Video Files (*.xlsx);;All Files (*)")
        if file_name:
            self.file_path.setText(file_name)
            self.log_text.append(f'已选择文件: {file_name}')
            # 保存当前选择的文件路径
            self.settings.setValue('last_file_path', file_name)

    def open_directory(self):
        dir_name = QFileDialog.getExistingDirectory(self, "选择输出目录", "")
        if dir_name:
            self.output_path.setText(dir_name)
            self.log_text.append(f'已选择输出目录: {dir_name}')


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
