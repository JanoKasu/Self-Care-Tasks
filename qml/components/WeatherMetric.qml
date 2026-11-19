import QtQuick
import QtQuick.Layouts
import ".." as AppTheme

ColumnLayout {
    required property string icon
    required property string label
    required property string value

    spacing: 2

    Text {
        text: icon + " " + label
        color: AppTheme.Theme.textSecondary
        font.pixelSize: 11
    }

    Text {
        text: value
        color: AppTheme.Theme.textPrimary
        font.pixelSize: 14
        font.bold: true
    }
}
