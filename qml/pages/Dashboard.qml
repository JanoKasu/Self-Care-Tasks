import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import ".." as AppTheme

Item {
    id: root

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0; color: AppTheme.Theme.canvas }
            GradientStop { position: 1; color: AppTheme.Theme.canvasAlt }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 18

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                spacing: 3

                Text {
                    text: "Today's Tasks"
                    font.pixelSize: 28
                    font.bold: true
                    color: AppTheme.Theme.textPrimary
                }

                Text {
                    text: "Small steps. Big difference."
                    font.pixelSize: 14
                    color: AppTheme.Theme.textSecondary
                }
            }

            Item {
                Layout.fillWidth: true
            }

            Rectangle {
                Layout.preferredWidth: 132
                Layout.preferredHeight: 52
                radius: 18
                color: AppTheme.Theme.accent

                Text {
                    anchors.centerIn: parent
                    text: "+ Add task"
                    color: "white"
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                }

                TapHandler {
                    onTapped: addTaskDialog.open()
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 82
            radius: 18
            color: AppTheme.Theme.surface
            border.width: 1
            border.color: AppTheme.Theme.divider

            ColumnLayout {
            anchors.fill: parent
            anchors.leftMargin: 18
            anchors.rightMargin: 18
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8

            RowLayout {
                Layout.fillWidth: true

                Text {
                    text: taskModel.completedCount + " of " + taskModel.count + " complete"
                    color: AppTheme.Theme.textPrimary
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: taskModel.progress + "%"
                    color: AppTheme.Theme.accent
                    font.pixelSize: 14
                    font.bold: true
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 8
                radius: 4
                color: AppTheme.Theme.progressTrack

                Rectangle {
                    width: parent.width * taskModel.progress / 100
                    height: parent.height
                    radius: parent.radius
                    color: AppTheme.Theme.accentLight

                    Behavior on width {
                        NumberAnimation { duration: 180 }
                    }
                }
            }
            }
        }

        ScrollView {
            id: taskScrollView

            Layout.fillWidth: true
            Layout.fillHeight: true

            clip: true

            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            GridLayout {
                width: taskScrollView.availableWidth

                columns: width < 560 ? 1 : 2
                rowSpacing: 14
                columnSpacing: 14

                Repeater {
                    model: taskModel

                    delegate: TaskCard {
                        // Database model data
                        title: model.title
                        description: model.description
                        taskIcon: model.taskIcon
                        impact: model.impact
                        backgroundColor: model.backgroundColor
                        completed: model.completed
                        createdAt: model.createdAt

                        Layout.fillWidth: true
                        Layout.preferredHeight: 156

                        onCompletionRequested: function(isCompleted) {
                            taskModel.setCompleted(
                                model.taskId,
                                isCompleted
                            )
                        }
                    }
                }
            }
        }
    }

    Dialog {
        id: addTaskDialog
        anchors.centerIn: parent
        modal: true
        title: "Add a self-care task"
        width: Math.min(root.width - 48, 420)
        footer: DialogButtonBox {
            buttonLayout: DialogButtonBox.AndroidLayout
            standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel
            delegate: Button {
                implicitHeight: 52
                implicitWidth: 112
                font.pixelSize: 15
            }

            onAccepted: addTaskDialog.accept()
            onRejected: addTaskDialog.reject()
        }

        ColumnLayout {
            width: parent.width
            spacing: 12

            TextField {
                id: titleField
                Layout.fillWidth: true
                Layout.preferredHeight: 54
                placeholderText: "Task name"
                font.pixelSize: 16
            }

            TextField {
                id: descriptionField
                Layout.fillWidth: true
                Layout.preferredHeight: 54
                placeholderText: "Short description"
                font.pixelSize: 16
            }

            ComboBox {
                id: impactField
                Layout.fillWidth: true
                Layout.preferredHeight: 54
                model: ["Low", "Medium", "High"]
                font.pixelSize: 16
            }
        }

        onOpened: titleField.forceActiveFocus()
        onAccepted: {
            if (taskModel.addTask(
                    titleField.text,
                    descriptionField.text,
                    "Anytime",
                    AppTheme.Theme.taskMint,
                    impactField.currentText,
                    "🌿")) {
                titleField.text = ""
                descriptionField.text = ""
                impactField.currentIndex = 1
            }
        }
    }
}
