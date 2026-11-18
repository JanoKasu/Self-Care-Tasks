import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as AppTheme

Dialog {
    id: root

    property string icon: ""
    property string subtitle: ""

    modal: true
    width: Math.min(parent.width - 40, 460)
    padding: 24
    leftPadding: 24
    rightPadding: 24
    bottomPadding: 22
    focus: true

    background: Rectangle {
        radius: 26
        color: AppTheme.Theme.surface
        border.width: 1
        border.color: AppTheme.Theme.divider

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 7
            color: AppTheme.Theme.accentLight
            radius: parent.radius

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: parent.height / 2
                color: parent.color
            }
        }
    }

    header: Item {
        implicitWidth: parent.width
        implicitHeight: titleRow.implicitHeight + 42

        RowLayout {
            id: titleRow
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.leftMargin: 24
            anchors.rightMargin: 24
            anchors.topMargin: 24
            spacing: 14

            Rectangle {
                visible: root.icon !== ""
                Layout.preferredWidth: 48
                Layout.preferredHeight: 48
                radius: 15
                color: AppTheme.Theme.canvasAlt

                Text {
                    anchors.centerIn: parent
                    text: root.icon
                    color: AppTheme.Theme.accent
                    font.pixelSize: 22
                    font.bold: true
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 3

                Text {
                    Layout.fillWidth: true
                    text: root.title
                    color: AppTheme.Theme.textPrimary
                    font.pixelSize: 21
                    font.bold: true
                    wrapMode: Text.WordWrap
                }

                Text {
                    visible: root.subtitle !== ""
                    Layout.fillWidth: true
                    text: root.subtitle
                    color: AppTheme.Theme.textSecondary
                    font.pixelSize: 13
                    wrapMode: Text.WordWrap
                }
            }
        }
    }

    Overlay.modal: Rectangle {
        color: "#493D5C"
        opacity: 0.52
    }

    enter: Transition {
        NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 140 }
        NumberAnimation { property: "scale"; from: 0.96; to: 1; duration: 180 }
    }

    exit: Transition {
        NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 120 }
    }
}
