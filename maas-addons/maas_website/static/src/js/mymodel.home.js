$(document).ready(function(){
    get_home_report_bi()
    function get_home_report_bi(){
        $.ajax({
            dataType: 'json',
            url: '/report/' + parseInt($('#partner_id').val()) + '/res_partner',
            type: 'POST',
            proccessData: false,
            data: {},
        }).then(function (records) {
            var data = records.reduce(function (a, b) {
                a.push({id: b['id'], report_bi_src: b['report_bi_src'],});
                return a;
            }, []);
            $('#home_report_bi_src').attr('srcdoc', data[0]['report_bi_src']);
        });
    }
})