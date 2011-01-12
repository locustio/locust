uki([
    {
        view: 'Button',
        rect: '450 30 200 24',
        text: 'Start swarming'
    },
    { view: 'Label', rect: '0 10 200 50', text: 'Locust', style: {fontSize: '45px', fontFamily: 'Palatino'}},
    { view: 'Label', rect: '10 40 200 50', text: '- Scalable user load simulator for humans', style: {fontSize: '15px', fontFamily: 'Palatino'}},
    { view: 'Table', rect: '0 90 700 300', minSize: '0 200', anchors: 'left top right bottom', columns: [
        { view: 'table.CustomColumn', label: 'Name', resizable: true, minWidth: 100, width: 350  },
        { view: 'table.NumberColumn', label: '# requests', resizable: true, width: 80 },
        { view: 'table.NumberColumn', label: 'Average', resizable: true, minWidth: 70, width: 70 },
        { view: 'table.NumberColumn', label: 'Min', resizable: true, minWidth: 50, width: 50 },
        { view: 'table.NumberColumn', label: 'Max', resizable: true, minWidth: 50, width: 50 },
        { view: 'table.NumberColumn', label: '# reqs/sec', resizable: true, width: 100 },
    ], multiselect: false, style: {fontSize: '12px', lineHeight: '12px'} }

]).attachTo( document.getElementById('content'), '700 100' );

uki('Button[text^=Start]').bind('click', function() {
    console.log('Swarming');
    $.get('/swarm');
    updateStats();
});

var table = uki('Table');
function updateStats() {
    $.get('/stats/requests', function (data) {
        table.data(eval(data));
        setTimeout(updateStats, 1000);
    });
}

