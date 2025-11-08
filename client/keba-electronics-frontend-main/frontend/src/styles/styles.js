import { makeStyles } from '@material-ui/styles';

const useStyles = makeStyles({
  tableContainer: {
    marginTop: 20,
  },
  table: {
    minWidth: 650,
  },
  tableHeaderCell: {
    fontWeight: 'bold',
    backgroundColor: '#f0f0f0',
  },
  tableBodyCell: {
    textAlign: 'right',
  },
});

export { useStyles };
