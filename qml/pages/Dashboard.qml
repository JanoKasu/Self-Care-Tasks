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
                visible: root.width >= 650
                Layout.preferredWidth: 94
                Layout.preferredHeight: 44
                radius: 22
                color: AppTheme.Theme.surface
                border.width: 1
                border.color: AppTheme.Theme.divider

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 6

                    Text {
                        text: "★"
                        color: AppTheme.Theme.landingGold
                        font.pixelSize: 18
                    }

                    Text {
                        text: "Level " + taskModel.level
                        color: AppTheme.Theme.textPrimary
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                    }
                }
            }

            ActionButton {
                Layout.preferredWidth: 132
                Layout.preferredHeight: 52
                text: "+ Add task"
                primary: true
                Accessible.name: "Add a self-care task"
                onClicked: addTaskDialog.open()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 94
            radius: 18
            color: AppTheme.Theme.surface
            border.width: 1
            border.color: AppTheme.Theme.divider

            RowLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 18

                ColumnLayout {
                    Layout.fillWidth: true
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

                Rectangle {
                    Layout.preferredWidth: 1
                    Layout.fillHeight: true
                    color: AppTheme.Theme.divider
                }

                ColumnLayout {
                    Layout.preferredWidth: 190
                    spacing: 7

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: taskModel.xp + " XP"
                            color: AppTheme.Theme.textPrimary
                            font.pixelSize: 16
                            font.bold: true
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: taskModel.pointsToNextLevel + " to go"
                            color: AppTheme.Theme.textSecondary
                            font.pixelSize: 11
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 8
                        radius: 4
                        color: AppTheme.Theme.progressTrack

                        Rectangle {
                            width: parent.width * taskModel.levelProgress / 100
                            height: parent.height
                            radius: parent.radius
                            color: AppTheme.Theme.landingGold

                            Behavior on width {
                                NumberAnimation { duration: 180 }
                            }
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
                id: taskGrid
                objectName: "taskGrid"
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
                        frequency: model.frequency
                        points: model.points
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

                Item {
                    visible: taskModel.count === 0
                    Layout.columnSpan: taskGrid.columns
                    Layout.fillWidth: true
                    Layout.preferredHeight: 220

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 10

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "+"
                            color: AppTheme.Theme.accent
                            font.pixelSize: 38
                            font.bold: true
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Start with one small step"
                            color: AppTheme.Theme.textPrimary
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Add a self-care task to begin building your routine."
                            color: AppTheme.Theme.textSecondary
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                        }

                        ActionButton {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Add your first task"
                            primary: true
                            onClicked: addTaskDialog.open()
                        }
                    }
                }
            }
        }
    }

    Timer {
        id: rewardTimer
        interval: 2500
        onTriggered: rewardToast.visible = false
    }

    Rectangle {
        id: rewardToast
        visible: false
        z: 10
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 18
        width: Math.min(parent.width - 32, 360)
        height: 58
        radius: 18
        color: AppTheme.Theme.accent

        Text {
            anchors.centerIn: parent
            text: "Nice work! +" + root.rewardPoints + " XP"
                  + (root.leveledUp ? "  •  Level " + taskModel.level + " unlocked!" : "")
            color: AppTheme.Theme.surface
            font.pixelSize: 15
            font.weight: Font.DemiBold
        }
    }

    property int rewardPoints: 0
    property bool leveledUp: false

    Connections {
        target: taskModel
        function onRewardEarned(points, level, isLevelUp) {
            root.rewardPoints = points
            root.leveledUp = isLevelUp
            rewardToast.visible = true
            rewardTimer.restart()
        }
    }

    AppDialog {
        id: addTaskDialog
        objectName: "addTaskDialog"
        anchors.centerIn: parent
        width: Math.min(root.width - 40, 600)
        title: "Add a self-care task"
        icon: "+"
        subtitle: "Choose a schedule and priority for your next small step."
        footer: Item {
            implicitHeight: 68

            RowLayout {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.rightMargin: 24
                spacing: 10

                ActionButton {
                    text: "Cancel"
                    onClicked: addTaskDialog.reject()
                }

                ActionButton {
                    text: "Add task"
                    primary: true
                    enabled: titleField.text.trim().length > 0
                    onClicked: addTaskDialog.accept()
                }
            }
        }

        ColumnLayout {
            width: parent.width
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    spacing: 6

                    Text {
                        text: "Task name"
                        color: AppTheme.Theme.textSecondary
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }

                    TextField {
                        id: titleField
                        Layout.fillWidth: true
                        Layout.preferredHeight: 50
                        placeholderText: "e.g. Brush teeth"
                        font.pixelSize: 16
                        color: AppTheme.Theme.textPrimary
                        background: Rectangle {
                            radius: 14
                            color: titleField.activeFocus
                                  ? AppTheme.Theme.surface
                                  : AppTheme.Theme.canvas
                            border.width: titleField.activeFocus ? 2 : 1
                            border.color: titleField.activeFocus
                                         ? AppTheme.Theme.accentLight
                                         : AppTheme.Theme.divider
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    spacing: 6

                    Text {
                        text: "Note (optional)"
                        color: AppTheme.Theme.textSecondary
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }

                    TextField {
                        id: descriptionField
                        Layout.fillWidth: true
                        Layout.preferredHeight: 50
                        placeholderText: "A helpful detail"
                        font.pixelSize: 15
                        color: AppTheme.Theme.textPrimary
                        background: Rectangle {
                            radius: 14
                            color: descriptionField.activeFocus
                                  ? AppTheme.Theme.surface
                                  : AppTheme.Theme.canvas
                            border.width: descriptionField.activeFocus ? 2 : 1
                            border.color: descriptionField.activeFocus
                                         ? AppTheme.Theme.accentLight
                                         : AppTheme.Theme.divider
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5

                    Text {
                        text: "Frequency"
                        color: AppTheme.Theme.textSecondary
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }

                    FieldComboBox {
                        id: frequencyField
                        Layout.fillWidth: true
                        Layout.preferredHeight: 50
                        model: ["Daily", "Weekly", "Monthly"]
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5

                    Text {
                        text: "Priority"
                        color: AppTheme.Theme.textSecondary
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }

                    FieldComboBox {
                        id: impactField
                        Layout.fillWidth: true
                        Layout.preferredHeight: 50
                        model: ["Low", "Medium", "High"]
                        currentIndex: 1
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 38
                radius: 12
                color: AppTheme.Theme.taskMint

                Text {
                    anchors.fill: parent
                    anchors.margins: 12
                    text: frequencyField.currentText + " task · "
                          + impactField.currentText + " priority · +"
                          + (impactField.currentText === "High"
                             ? 30
                             : impactField.currentText === "Medium" ? 20 : 10)
                          + " XP"
                    verticalAlignment: Text.AlignVCenter
                    color: AppTheme.Theme.impactMedium
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                }
            }
        }

        onOpened: titleField.forceActiveFocus()
        onAccepted: {
            if (taskModel.addTaskWithFrequency(
                    titleField.text,
                    descriptionField.text,
                    "Anytime",
                    AppTheme.Theme.taskMint,
                    impactField.currentText,
                    "🌿",
                    frequencyField.currentText)) {
                titleField.text = ""
                descriptionField.text = ""
                impactField.currentIndex = 1
                frequencyField.currentIndex = 0
            }
        }
    }
}
