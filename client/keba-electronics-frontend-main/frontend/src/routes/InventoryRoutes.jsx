import { Routes, Route } from 'react-router-dom';
import Components from '../pages/Inventory/Components';
import ComponentForm from '../pages/Inventory/ComponentForm';
import ComponentDetails from '../pages/Inventory/ComponentDetails';
import PRs from '../pages/Inventory/PRs';
import POs from '../pages/Inventory/POs';
import PRForm from '../pages/Inventory/PRForm';
import POForm from '../pages/Inventory/POForm';
import POEdit from '../pages/Inventory/POEdit';
import PRView from '../pages/Inventory/PRView';
import POView from '../pages/Inventory/PurchaseOrder/POView';
import InventoryReport from '../pages/Reports/InventoryReport';
import Suppliers from '../pages/Inventory/Suppliers/Suppliers';
import SupplierForm from '../pages/Inventory/Suppliers/SupplierForm';

const InventoryRoutes = () => (
  <Routes>
    <Route path="/component" element={<Components />} />
    <Route path="/component/new" element={<ComponentForm />} />
    <Route path="/component/:id" element={<ComponentDetails />} />
    <Route path="/purchase-req" element={<PRs />} />
    

    <Route path="/purchase-requisition/new" element={<PRForm />} />

    
    <Route path="/purchase-requisition/:id" element={<PRView />} />

    <Route path="/po" element={<POs />} />
    <Route path="/purchase-order/new" element={<POForm />} />
    <Route path="/purchase-order/edit/:id" element={<POEdit />} />
    <Route path="/purchase-order/:id" element={<POView />} />

    <Route path="/suppliers" element={<Suppliers />} />
    <Route path="/supplier/new" element={<SupplierForm />} />

    <Route path="/inventory-reports" element={<InventoryReport />} />
  </Routes>
);

export default InventoryRoutes;
