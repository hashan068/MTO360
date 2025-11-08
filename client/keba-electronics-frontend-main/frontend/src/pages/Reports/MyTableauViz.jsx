import React, { useEffect, useRef } from 'react';

const MyTableauViz = () => {
  const vizContainerRef = useRef(null);

  useEffect(() => {
    // Initialize the Tableau visualization
    const initViz = () => {
      if (!window.tableau) {
        console.error('Tableau JavaScript API not loaded');
        return;
      }
    
      const vizUrl = 'https://prod-apnortheast-a.online.tableau.com/t/dhananjim20068d4e922f96c/views/Book2/Dashboard1';
      const vizOptions = {
        width: '1000px',
        height: '840px',
        hideTabs: true,
        toolbarPosition: 'bottom',
      };
    
      const viz = new window.tableau.Viz(vizContainerRef.current, vizUrl, vizOptions);
    };

    // Load the Tableau JavaScript API
    const script = document.createElement('script');
    script.src = 'https://prod-apnortheast-a.online.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js';
    script.onload = initViz;
    document.body.appendChild(script);

    // Clean up the script element on component unmount
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return <div ref={vizContainerRef} />;
};

export default MyTableauViz;