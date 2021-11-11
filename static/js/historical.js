//Click handler for reopen tests
$('#data_table_2').on('click', '#reopen', function(){
    var row_id = $(this)[0].getAttribute("value");

    var http = new XMLHttpRequest();
    var url = '/api/reopen';
    var params = 'id=' +row_id;
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {//Call a function when the state changes.
        if(http.readyState == 4 && http.status == 200) {
            makeAPIRequest('api/historical', displayHistoricalTests);
        }
    }
    http.send(params);
});



//Global resize functionality
window.onresize = function(event) {
    $('#data_table_2').dataTable().fnAdjustColumnSizing();

};


//Change
function changePage(page, first){
    var pages = document.getElementsByClassName("page");
    for(element of pages){
        console.log(element.id);
        if(element.id == page + "-page"){
            element.classList.remove("hidden");
        }
        else{
            element.classList.add("hidden");

        }
    }
    if(!first){
        $('#data_table_1').dataTable().fnAdjustColumnSizing();
        $('#data_table_2').dataTable().fnAdjustColumnSizing();
    }

}

function makeAPIRequest(endpoint, callback){
    let request = new XMLHttpRequest();
    request.open("GET", endpoint);
    request.send();
    request.onload = () => {
        console.log(request);
        if(request.status == 200){
            callback(request.response);
        }
        else{
            console.log("ERROR IN API REQUEST!");
        }

    }
}

function displayHistoricalTests(response){
    $('#data_table_2').DataTable().destroy()

    var table = document.getElementById("open_body_historical");
    table.innerHTML = ""
    table_string = "";
    row_count = 1;
    json_response = JSON.parse(response);
    json_response.forEach(obj => {
            table_string += "<tr value='" + obj.id + "'>"
            +"<th scope='row'>"+ row_count + "</th>"
                +"<td>"+ obj.company + "</td>"
                +"<td>"+ obj.terminal + "</td>"
                +"<td>" + obj.driver_code + "</td>"
                +"<td>" + obj.name + "</td>"
                +"<td>" + obj.test_type + "</td>"
                +"<td>" + obj.date + "</td>"
                +"<td>" + obj.hire_date + "</td>"
                +"<td>" + obj.return_date + "</td>"
                +"<td class='" + obj.result + "'>" + obj.result + "</td>"
                +"<td><button id='reopen' value='" + obj.id + "' class='btn btn-sm btn-primary'>Reopen</button></td>"

            +"</tr>";
            row_count++;
    });
    table.innerHTML = table_string;
    
    $('#data_table_2').DataTable(
        {
            "scrollY":"60vh",
            "sScrollX": "100%",

            "scrollCollapse": true,
            "autoWidth":true
        }
    );
   
}

makeAPIRequest('api/historical', displayHistoricalTests);
