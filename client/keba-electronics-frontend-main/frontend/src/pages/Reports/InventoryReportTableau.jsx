import React, { useEffect } from 'react';

const InventoryReportTableau = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'module';
    script.src = 'https://prod-apnortheast-a.online.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js';
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div
      style={{
        alignItems: 'center',
        display: 'flex',
        justifyContent: 'center',
        flexDirection: 'column',
      }}
    >
      <h1>Inventory Report</h1>
      <tableau-viz
        id='tableau-viz'
        src='https://prod-apnortheast-a.online.tableau.com/t/dhananjim20068d4e922f96c/views/InventoryReport/MonthlyInventoryReport'
        width='1000'
        height='840'
        hide-tabs
        toolbar='bottom'
      ></tableau-viz>
    </div>
  );
};

export default InventoryReportTableau;
