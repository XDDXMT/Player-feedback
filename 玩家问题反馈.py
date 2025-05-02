from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt
import sys

class FeedbackGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("玩家反馈回复生成器")
        self.setFixedSize(720, 700)
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #eef5ee;
        #         font-family: 'Microsoft YaHei';
        #         font-size: 14px;
        #     }
        #     QLineEdit, QTextEdit, QComboBox {
        #         background-color: #ffffff;
        #         border: 1px solid #ccc;
        #         border-radius: 5px;
        #         padding: 6px;
        #     }
        #     QPushButton {
        #         background-color: #4CAF50;
        #         color: white;
        #         padding: 8px 16px;
        #         border: none;
        #         border-radius: 6px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background-color: #45a049;
        #     }
        # """)

        layout = QVBoxLayout()
        layout.setSpacing(14)

        self.template_box = self.create_combo_box("📝 选择模板", [
            "（请选择模板）",
            "✅ 已完成",
            "❌ 无法解决",
            "🤔 问题不存在 / 无效反馈",
            "📩 收到反馈（确认存在）"
        ])
        self.template_box[1].currentIndexChanged.connect(self.toggle_inputs)
        layout.addWidget(self.template_box[0])
        layout.addWidget(self.template_box[1])

        layout.addWidget(self.line_separator())

        self.name_input = self.create_input("🎮 玩家名（如：@Steve）", layout)
        self.feedback_input = self.create_text_edit("🗣️ 用户反馈内容", layout)
        self.summary_input = self.create_text_edit("🧾 自己总结", layout)
        self.days_input = self.create_input("⏱️ 尝试修复时间（直接写数字不用写天） / 耗时（如：1~3天）", layout)
        self.reason_input = self.create_text_edit("📌 无法修复的原因", layout)

        layout.addWidget(self.line_separator())

        layout.addWidget(self.bold_label("📬 生成的回复内容"))
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        btn_layout = QHBoxLayout()
        generate_btn = QPushButton("🚀 生成回复")
        generate_btn.clicked.connect(self.generate_reply)
        copy_btn = QPushButton("📋 复制")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(generate_btn)
        btn_layout.addWidget(copy_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.toggle_inputs()  # 初始化隐藏无关字段

    def create_combo_box(self, label_text, items):
        label = self.bold_label(label_text)
        combo = QComboBox()
        combo.addItems(items)
        return label, combo

    def create_input(self, label_text, layout):
        label = self.bold_label(label_text)
        input_field = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(input_field)
        return (label, input_field)

    def create_text_edit(self, label_text, layout):
        label = self.bold_label(label_text)
        input_field = QTextEdit()
        layout.addWidget(label)
        layout.addWidget(input_field)
        return (label, input_field)

    def bold_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        return label

    def line_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #bbb;")
        return line

    def toggle_inputs(self):
        template = self.template_box[1].currentText()
        # 全部隐藏
        for pair in [self.summary_input, self.reason_input, self.days_input, self.feedback_input]:
            pair[0].hide()
            pair[1].hide()
        # 再按需显示
        if template == "✅ 已完成":
            self.days_input[0].show();self.days_input[1].show()
            self.feedback_input[0].show(); self.feedback_input[1].show()
        elif template == "❌ 无法解决":
            self.feedback_input[0].show();self.feedback_input[1].show()
            self.days_input[0].show(); self.days_input[1].show()
            self.reason_input[0].show(); self.reason_input[1].show()
        elif template == "🤔 问题不存在 / 无效反馈":
            self.feedback_input[0].show();self.feedback_input[1].show()
            self.reason_input[0].show(); self.reason_input[1].show()
        elif template == "📩 收到反馈（确认存在）":
            self.feedback_input[0].show(); self.feedback_input[1].show()
            self.days_input[0].show(); self.days_input[1].show()

    def generate_reply(self):
        template = self.template_box[1].currentText()
        name = self.name_input[1].text().strip()
        feedback = self.feedback_input[1].toPlainText().strip()
        summary = self.summary_input[1].toPlainText().strip()
        days = self.days_input[1].text().strip()
        reason = self.reason_input[1].toPlainText().strip()

        if template == "（请选择模板）":
            QMessageBox.warning(self, "请选择模板", "请先选择一个回复模板。")
            return

        if not name:
            QMessageBox.warning(self, "缺少玩家名", "请填写玩家名（@xxx）")
            return

        if template == "✅ 已完成":
            if not feedback or not days:
                QMessageBox.warning(self, "缺少反馈内容", "请填写反馈内容。")
                return
            reply = f"""\
您好，玩家 {name}：

经过管理们 {days} 的修复，该问题已被确认为已修复！
我们已解决您的反馈：{feedback}

再次感谢您细致的反馈与支持，您的建议是我们不断优化的重要动力！
"""

        elif template == "❌ 无法解决":
            if not feedback or not days or not reason:
                QMessageBox.warning(self, "信息不完整", "请填写反馈内容、耗时、失败原因。")
                return
            reply = f"""\
您好，玩家 {name}：

我们的技术团队在这 {days} 天内，努力尝试解决您提出的反馈：{feedback}
但是多次尝试解决该问题无果，该问题无法修复，大致原因：{reason}
修复难度评级：国道百吨王都创不碎的BUG

在此，我代表全服各大管理员向玩家们说声：对不起！
再次感谢您细致的反馈与支持，您的建议是我们不断优化的重要动力！
"""

        elif template == "🤔 问题不存在 / 无效反馈":
            if not feedback or not reason:
                QMessageBox.warning(self, "信息不完整", "请填写总结与不存在原因。")
                return
            reply = f"""\
您好，玩家 {name}：

我们已成功接收到您的反馈，内容概括如下：
{feedback}

经确认，该问题并不存在。请检查是否为您客户端的问题：
{reason}

请提供有效的反馈，您的建议是我们不断优化的重要动力！
"""

        elif template == "📩 收到反馈（确认存在）":
            if not feedback or not days:
                QMessageBox.warning(self, "信息不完整", "请填写总结和预计修复时间。")
                return
            reply = f"""\
您好，玩家 {name}：

我们已成功接收到您的反馈，内容概括如下：
{feedback}

经确认，该问题确实存在。我们已将其列入修复计划，预计将在 {days} 内完成修复工作。
感谢您细致的反馈与支持，您的建议是我们不断优化的重要动力！
"""

        else:
            reply = "模板未知或未处理。"

        self.result_box.setText(reply)
        self.result_box.moveCursor(QTextCursor.Start)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.result_box.toPlainText())
        QMessageBox.information(self, "已复制", "回复内容已复制到剪贴板！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FeedbackGenerator()
    window.show()
    sys.exit(app.exec())
