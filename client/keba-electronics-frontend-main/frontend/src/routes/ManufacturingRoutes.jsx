import { Routes, Route } from 'react-router-dom';
import ManufacturingOrder from '../pages/Manufacturing/ManufacturingOrder';
import MfgOrderDetails from '../pages/Manufacturing/MfgOrderDetails';
import MaterialReq from '../pages/Manufacturing/MaterialReq/MaterialReq';
import MaterialReqDetails from '../pages/Manufacturing/MaterialReq/MaterialReqDetails';
import BOMs from '../pages/Manufacturing/BOMS/BOMs';
import AddBOMForm from '../pages/Manufacturing/BOMS/AddBOMForm';
import ViewBOM from '../pages/Manufacturing/BOMS/ViewBOM';
import ManufacturingReport from '../pages/Reports/ManufacturingReport';

const ManufacturingRoutes = () => (
  <Routes>
    <Route path="/mfgorder" element={<ManufacturingOrder />} />
    <Route path="/mfgorder/:id" element={<MfgOrderDetails />} />
    <Route path="/bom" element={<BOMs />} />
    <Route path="/bom/new" element={<AddBOMForm />} />
    <Route path="/bom/:id" element={<ViewBOM />} />
    <Route path="/materialreq" element={<MaterialReq />} />
    <Route path="/materialreq/:id" element={<MaterialReqDetails />} />
    <Route path="/mfg-reports" element={<ManufacturingReport />} />
    
  </Routes>
);

export default ManufacturingRoutes;
