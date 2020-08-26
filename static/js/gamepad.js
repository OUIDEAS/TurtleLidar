function gamepadLoop(controller, readToggle, last_press, last_pressB) { // reference: https://github.com/luser/gamepadtest/blob/master/gamepadtest.js
    var val = controller.buttons[1];
    var pressed = val == 1.0;
    if (typeof(val) == "object") {
        pressed = val.pressed;
        val = val.value;
    }
    //console.log('button state ' + pressed)
    if (pressed && last_pressB != pressed) {
        readToggle = !readToggle;

        // change state display
        var stateText = '';
        if (readToggle) {
            stateText = "Status: Reading Input (press 'B' to stop).";
        } else {
            stateText = "Status: Waiting (press 'B' to start).";
        }
        $('#controller-status').text(stateText);
    }
    last_pressB = pressed;

    if (readToggle) {
        var aBtnId = 0
        val = controller.buttons[aBtnId];
        pressed = val == 1.0;
        if (typeof(val) == "object") {
            pressed = val.pressed;
            val = val.value;
        }
        //console.log('A-button pressed: ' + pressed);
        // change a btn display value
        if (pressed && pressed != last_press) {
            $('#ctrl-a-btn-val').text('Pressed')

            // a btn api call
            // $.post('/api/test', {asdf:'test data! :)'}).done(function(response) {
            //     alert(response)
            // });
            $.ajax({
                type: "POST",
                url: "/api/scan",
                data: {'hello': 'test :)', 'world': 0.001},
                complete: function(data) {
                    // alert(data.responseText);
                },
                error: function(e) {
                    console.log('Failed API call...');
                    console.log(e)
                },
                dataType: "application/json;charset=UTF-8"
            });
        } else {
            $('#ctrl-a-btn-val').text('Not Pressed')
        }
        last_press = pressed;
        
        var i = 0 // left stick, left-right
        //console.log("Axis: " + String(i));
        lrAxis = controller.axes[i]
        //console.log(lrAxis.toFixed(4));
        //console.log(lrAxis);
        // change lr display value
        $('#ctrl-lr-val').text(lrAxis.toFixed(4))

        i = 1 // left stick, up-down (invert sign)
        //console.log("Axis: " + String(i));
        udAxis = -controller.axes[i]
        //console.log(udAxis.toFixed(4));
        //console.log(udAxis);
        // change ud display value
        $('#ctrl-ud-val').text(udAxis.toFixed(4))

        // joystick api call
        $.ajax({
            type: "POST",
            url: "/api/drive",
            data: {'lr': lrAxis, 'ud': udAxis},
            complete: function(data) {
                console.log(data.responseText);
            },
            error: function(e) {
                console.log('Failed API call...');
                console.log(e)
            },
            dataType: "application/json;charset=UTF-8"
        });


    } else {
        //console.log('Inactive.');
    }

    setTimeout(function(){gamepadLoop(controller, readToggle, last_press, last_pressB);}, 50);
}

//console.log('waiting for ctrl input')
window.addEventListener("gamepadconnected", function(e) {
    var gp = navigator.getGamepads()[e.gamepad.index];
    console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
    gp.index, gp.id,
    gp.buttons.length, gp.axes.length);
    $('#controller-status').text("Status: Reading Input (press 'B' to stop).");
    gamepadLoop(gp, true, false, false);
});