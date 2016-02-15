$(document).ready(function() {
  // User page - Send deviceId to the device properties modal
  $('#editDevice').on('shown.bs.modal', function(e) {
    var deviceId = $(e.relatedTarget).data('device-id'); $(e.currentTarget).find('input[name="deviceId"]').val(deviceId);
    var deviceName = $(e.relatedTarget).data('device-name'); $(e.currentTarget).find('input[name="newName"]').val(deviceName);
    var deleteDeviceURL = $(e.relatedTarget).data('delete-device-url'); document.getElementById('deleteDevice').href = deleteDeviceURL; 
    var renameDeviceURL = $(e.relatedTarget).data('rename-device-url'); document.getElementById('renameDevice').action = renameDeviceURL; 
  });
});
