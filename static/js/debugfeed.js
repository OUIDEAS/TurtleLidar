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
                var table = document.getElementById("debugtable");
                var jdata = data;
                if(jdata[0]['status'] != 'nothingnew')
                {
                    for (var i = 1;i < jdata.length;i++)
                    {
                        var row = jdata[i]

                        var tr = table.insertRow(-1);
                        var td = tr.insertCell(-1);
                        td.innerHTML = row[1];

                        var tabCell = tr.insertCell(-1);
                        tabCell.innerHTML = row[2];
                        lastID = row[0];

                        table.appendChild(tr);
                    }
                    //console.log(data);
                    console.log(lastID);
                }
                else
                    console.log("No new debug data");

                setTimeout(checkStatus,500);
            }
        });
    }
    setTimeout(checkStatus, 500);
})