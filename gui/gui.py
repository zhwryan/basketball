import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QLineEdit, QProgressBar, QTextEdit, QVBoxLayout,
                             QHBoxLayout, QFileDialog)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('篮球视频分析系统')
        self.setGeometry(100, 100, 620, 500)

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建文件路径选择区域
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText('原文件路径')
        self.open_file_btn = QPushButton('打开文件')
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.open_file_btn)
        main_layout.addLayout(file_layout)

        # 创建输出路径选择区域
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText('输出文件路径')
        self.open_dir_btn = QPushButton('打开目录')
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.open_dir_btn)
        main_layout.addLayout(output_layout)

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

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)")
        if file_name:
            self.file_path.setText(file_name)
            self.log_text.append(f'已选择文件: {file_name}')

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
