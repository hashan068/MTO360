/**
 * Work Center Management Page
 * Main page component for work center management
 */
import { WorkCenterList } from '../components/WorkCenterList';

export const WorkCentersPage = () => {
  return (
    <div className="p-6">
      <WorkCenterList />
    </div>
  );
};

export default WorkCentersPage;

