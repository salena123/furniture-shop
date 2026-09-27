import { ProjectSteps } from '../../components/home/ProjectSteps';
import { FeaturedWorks } from '../../components/home/FeaturedWorks';
import { HeroCarousel } from '../../components/home/HeroCarousel';
export default function HomePage({ onEnquiry }) {
  return (
    <div className="home-page">
      <HeroCarousel onEnquiry={onEnquiry} />
      <FeaturedWorks onEnquiry={onEnquiry} />
      <ProjectSteps onEnquiry={onEnquiry} />
    </div>
  );
}
