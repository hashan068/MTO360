import React from 'react';
import { Box, Button } from '@mui/material';



const PreviewDownloadButtons = ({ onPreview, onDownload }) => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
      <Button
        variant="contained"
        color="primary"
        onClick={onPreview}
        sx={{ mr: 2 }}
      >
        Preview
      </Button>
      <Button variant="contained" color="secondary" onClick={onDownload}>
        Download
      </Button>
    </Box>
  );
};

export default PreviewDownloadButtons;