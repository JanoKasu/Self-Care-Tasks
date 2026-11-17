import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: root

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 18

        // Header
        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                spacing: 3

                Text {
                    text: "Today's Tasks"
                    font.pixelSize: 28
                    font.bold: true
                    color: "#493D5C"
                }

                Text {
                    text: "Small steps. Big difference."
                    font.pixelSize: 14
                    color: "#756A83"
                }
            }

            Item {
                Layout.fillWidth: true
            }

            Text {
                text: taskModel.count + " tasks"
                color: "#756A83"
                font.pixelSize: 14
            }
        }

        // Task list
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

                        Layout.fillWidth: true
                        Layout.preferredHeight: 145

                        // Save checkbox changes to SQLite
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
}
