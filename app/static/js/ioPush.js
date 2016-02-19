$(document).ready(function() {
  // User page - Send deviceId to the device properties modal
  $('#editDevice').on('shown.bs.modal', function(e) {
    var deviceId = $(e.relatedTarget).data('device-id'); $(e.currentTarget).find('input[name="deviceId"]').val(deviceId);
    var deviceName = $(e.relatedTarget).data('device-name'); $(e.currentTarget).find('input[name="newName"]').val(deviceName);
    var deleteDeviceURL = $(e.relatedTarget).data('delete-device-url'); document.getElementById('deleteDevice').href = deleteDeviceURL; 
    var renameDeviceURL = $(e.relatedTarget).data('rename-device-url'); document.getElementById('renameDevice').action = renameDeviceURL; 
  });
});


// Send a push notification to all user's devices
function pushTestAllDevices(url, authToken) {
  document.getElementById("pushTestAllDevices").innerHTML = "Sending...";
  
  $.ajax({
    type: "POST",
    url: url,
    data: JSON.stringify({ "body": "Test message", "push" : "True", "badge": "I" }),
    contentType: "application/json; charset=utf-8",
    headers: { 'authentication_token' : authToken },
    /*
    success: function(data){
      document.getElementById("pushTestAllDevices").innerHTML = "Send";
    },
    failure: function(errMsg) {
      document.getElementById("pushTestAllDevices").innerHTML = "Fail to reach server";
    },
    statusCode: {
      200: function(data) {
        if (data == 'ok') {
          document.getElementById("pushTestAllDevices").innerHTML = "Send !";
        } else {
          document.getElementById("pushTestAllDevices").innerHTML = "Fail";
        }
      },
      404: function() {
        document.getElementById("pushTestAllDevices").innerHTML = "Fail to reach the server";
      }
    }
    */
    complete: function(jqXHR, textStatus) {
      switch (jqXHR.status) {
        case 200:
          if (jqXHR.responseText  == 'ok') {
            document.getElementById("pushTestAllDevices").innerHTML = "Send !";
            break;
          }
        default:
          document.getElementById("pushTestAllDevices").innerHTML = "Failed";
      }
    }
  });  
}
