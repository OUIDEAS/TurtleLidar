$(document).ready(function() {
    function checkStatus(){
        $.ajax({
            type: "GET",
            url: "/scan_status",
            success: function(data){
                document.getElementById("scanstatus").innerHTML = data;
                console.log(data);
                setTimeout(checkStatus,500);
            }
        });
    }
    setTimeout(checkStatus, 500);
})