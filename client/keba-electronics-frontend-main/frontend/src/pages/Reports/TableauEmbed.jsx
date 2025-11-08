import React, { useEffect, useRef } from 'react';

const TableauEmbed = () => {
  const vizRef = useRef(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://prod-apnortheast-a.online.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js';
    script.type = 'module';
    script.onload = () => {
      // Wait for the Tableau script to load before initializing the viz
      initializeViz();
    };
    document.body.appendChild(script);

    const initializeViz = () => {
      if (!window.tableau || !window.tableau.Viz) {
        console.error('Tableau Viz object not found.');
        return;
      }
    
      const options = {
        hideTabs: true,
        toolbar: 'bottom',
        width: '1000px',
        height: '840px',
      };
    
      const vizUrl = 'https://prod-apnortheast-a.online.tableau.com/t/dhananjim20068d4e922f96c/views/Book2/Dashboard1';
      const containerDiv = vizRef.current;
    
      new window.tableau.Viz(containerDiv, vizUrl, options);
    };
    
    

    return () => {
      // Clean up the script and viz when the component unmounts
      document.body.removeChild(script);
      if (vizRef.current && vizRef.current.innerHTML) {
        vizRef.current.innerHTML = '';
      }
    };
  }, []);

  return <div ref={vizRef}></div>;
};

export default TableauEmbed;
