import QtQuick
import QtQuick.Controls
import ".." as AppTheme

ComboBox {
    id: root

    font.pixelSize: 15
    leftPadding: 16
    rightPadding: 42

    background: Rectangle {
        radius: 14
        color: root.activeFocus ? AppTheme.Theme.surface : AppTheme.Theme.canvas
        border.width: root.activeFocus ? 2 : 1
        border.color: root.activeFocus
                     ? AppTheme.Theme.accentLight
                     : AppTheme.Theme.divider
    }

    contentItem: Text {
        leftPadding: root.leftPadding
        rightPadding: root.rightPadding
        text: root.displayText
        color: AppTheme.Theme.textPrimary
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
        font: root.font
    }

    indicator: Text {
        anchors.right: parent.right
        anchors.rightMargin: 15
        anchors.verticalCenter: parent.verticalCenter
        text: "⌄"
        color: AppTheme.Theme.accent
        font.pixelSize: 18
        font.bold: true
    }

    delegate: ItemDelegate {
        width: root.width
        height: 46
        highlighted: root.highlightedIndex === index
        background: Rectangle {
            color: highlighted ? AppTheme.Theme.canvasAlt : AppTheme.Theme.surface
        }
        contentItem: Text {
            text: modelData
            leftPadding: 14
            verticalAlignment: Text.AlignVCenter
            color: AppTheme.Theme.textPrimary
            font: root.font
        }
    }
}
