$(document).ready(function() {
    var lastID = -1;
    function checkStatus(){
        $.ajax({
            type: "POST",
            url: "/debug_feed",
            contentType: "application/json",
            data: JSON.stringify({lastID: lastID}),
            dataType: "json",
            success: function(data){
                var showtimestamp = document.getElementById("showtimestamp");
                var table = document.getElementById("debugtable");
                var jdata = data;
                if(jdata[0]['status'] != 'nothingnew')
                {
                    //console.log(data);
                    for (var i = 0;i < jdata.length;i++)
                    {
                        var row = jdata[i]

                        var tr = table.insertRow(-1);
                        if(showtimestamp.checked) {
                            var td = tr.insertCell(-1);
                            td.innerHTML = row[1];
                        }
                        var tabCell = tr.insertCell(-1);
                        tabCell.innerHTML = row[2];
                        lastID = row[0];

                        table.appendChild(tr);
                        //console.log("Adding "+ row[0]);
                    }
                    //console.log(data);
                    //console.log(lastID);
                }
                else
                    console.log("No new debug data");
                if(document.getElementById('autoscroll').checked)
                    window.scrollTo(0,document.body.scrollHeight);
                setTimeout(checkStatus,500);
            }
        });
    }
    setTimeout(checkStatus, 500);
})