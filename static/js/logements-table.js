function compute_total_value(what, is_form=true){
    elements = document.querySelectorAll('[id=lgt_' + what + ']');
    total_value = 0;
    for ( i =0, len = elements.length; i<len; i++) {
        var inner_input = elements[i].getElementsByTagName('input')
        if (inner_input.length > 0) {
            total_value = total_value + parseFloat(inner_input[0].value);
        }
        else {
            let float = parseFloat(elements[i].innerHTML.replace(/,/, '.'));
            total_value = total_value + float;
        }
    }
    var total = document.getElementById('total_' + what)
    if (total !== null) {
        document.getElementById('total_' + what).innerHTML = "<span>" + total_value.toFixed(2).replace('.',',').replace(/\B(?=(\d{3})+(?!\d))/g, " ") + "</span>";
    }
}

compute_total_value('sh')
compute_total_value('sa')
compute_total_value('sar')
compute_total_value('su')
compute_total_value('loyer')

compute_total_value('sh_sl')
compute_total_value('sa_sl')
compute_total_value('sar_sl')
compute_total_value('su_sl')

compute_total_value('sh_sc')
compute_total_value('su_sc')
compute_total_value('loyer_sc')

compute_total_value('sh_scsl')
compute_total_value('su_scsl')