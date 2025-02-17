
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

const Breadcrumbs = () => {
  const location = useLocation();
  const paths = location.pathname.split('/').filter(Boolean);
  
  if (paths.length === 0) return null;

  return (
    <div className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
      {paths.map((path, index) => {
        const isLast = index === paths.length - 1;
        const formattedPath = path.split('-').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
        
        return (
          <div key={path} className="flex items-center">
            {index > 0 && <ChevronRight className="w-4 h-4 mx-2" />}
            {isLast ? (
              <span className="font-medium text-gray-900">{formattedPath}</span>
            ) : (
              <Link
                to={`/${paths.slice(0, index + 1).join('/')}`}
                className="hover:text-gray-900 transition-colors"
              >
                {formattedPath}
              </Link>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default Breadcrumbs;
