// src/SalesReportTableau.jsx
import React from 'react';
import { TableauEmbed } from '@stoddabr/react-tableau-embed-live';

const SalesReportTableau = () => {
  return (
    <div
      style={{
        alignItems: 'center',
        display: 'flex',
        justifyContent: 'center',
        flexDirection: 'column',
      }}
    >
      <h1>Sales Report</h1>
      <TableauEmbed 
        sourceUrl='https://prod-apnortheast-a.online.tableau.com/t/dhananjim20068d4e922f96c/views/Book2/Dashboard1'
        width='1000px'
        height='840px'
        hide-tabs
        // toolbar='bottom'
        toolbar='hidden'  
        // {/* This will hide the toolbar */}
      />
    </div>
  );
};

export default SalesReportTableau;
