function compute_total_value(what, is_form){
    elements = document.querySelectorAll('[id=lgt_' + what + ']');
    total_value = 0;
    for ( i =0, len = elements.length; i<len; i++) {
        total_value = total_value + parseFloat(elements[i].innerHTML.replace(',','.'));
    }
    document.getElementById('total_' + what).innerHTML = "<span>" + total_value.toFixed(2).replace('.',',').replace(/\B(?=(\d{3})+(?!\d))/g, " ") + "</span>";
}

compute_total_value('sh')
compute_total_value('sa')
compute_total_value('sar')
compute_total_value('su')
compute_total_value('loyer')
