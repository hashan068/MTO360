import { Routes, Route } from 'react-router-dom';
import Product from '../pages/Sales/Product';
import ProductDetails from '../pages/Sales/ProductDetails';
import SalesOrder from '../pages/Sales/SalesOrder';
import SalesOrderForm from '../pages/Sales/SalesOrderForm';
import SalesOrderDetails from '../pages/Sales/SalesOrderDetails';
import Quotations from '../pages/Sales/Quotations';
import QuotationDetail from '../pages/Sales/QuotationDetail';
import QuotationForm from '../pages/Sales/QuotationForm';
import Customers from '../pages/Sales/Customers';
import CustomerForm from '../pages/Sales/CustomerForm';
import CustomerDetail from '../pages/Sales/CustomerDetail';
import SalesReport from '../pages/Reports/SalesReport';
import ProductForm from '../pages/Sales/ProductForm';
import Insights from '../pages/Reports/Insights/Insights';

const SalesRoutes = () => (
  <Routes>
    <Route path="product" element={<Product />} />
    <Route path="product/new" element={<ProductForm />} />
    <Route path="product/:id" element={<ProductDetails />} />

    <Route path="customer" element={<Customers />} />
    <Route path="/customer/:id" element={<CustomerDetail />} />
    <Route path="customer/new" element={<CustomerForm />} />

    <Route path="quotations" element={<Quotations />} />
    <Route path="quotations/new" element={<QuotationForm />} />
    <Route path="quotation/:id" element={<QuotationDetail />} />
    <Route path="salesorder" element={<SalesOrder />} />
    <Route path="salesorder/new" element={<SalesOrderForm />} />
    <Route path="salesorder/:id" element={<SalesOrderDetails />} />
    <Route path="sales-reports" element={<SalesReport />} />

    <Route path="insights" element={<Insights />} />
  </Routes>
);

export default SalesRoutes;
