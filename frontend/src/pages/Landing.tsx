import React, { useContext, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatContext } from '../App';
import './Landing.css';

export const Landing: React.FC = () => {
  const navigate = useNavigate();
  const { setIsChatOpen } = useContext(ChatContext);
  const [isHeroVisible, setIsHeroVisible] = useState(false);
  const [visibleCards, setVisibleCards] = useState<{ [key: string]: boolean }>({});
  const sectionRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});

  // Animate hero on mount
  useEffect(() => {
    setIsHeroVisible(true);
  }, []);

  // Intersection Observer for scroll animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.getAttribute('data-section-id');
            if (id) {
              setVisibleCards((prev) => ({ ...prev, [id]: true }));
            }
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    Object.values(sectionRefs.current).forEach((ref) => {
      if (ref) observer.observe(ref);
    });

    return () => observer.disconnect();
  }, []);

  const setRef = (key: string, element: HTMLDivElement | null) => {
    sectionRefs.current[key] = element;
  };

  return (
    <div className="landing">
      {/* NAVBAR */}
      <nav className="navbar">
        <div className="navbar-container">
          <div className="navbar-logo">
            <span className="logo-icon">👁️</span>
            <span className="logo-text">RetinalCare</span>
          </div>
          <ul className="navbar-links">
            <li><a href="#about">About</a></li>
            <li><a href="#features">Features</a></li>
            <li><a href="#education" onClick={(e) => {
              e.preventDefault();
              setIsChatOpen(true);
            }}>Education</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
          <div className="navbar-buttons">
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/patient-lookup')}>
              Patient Portal
            </button>
            <button className="btn btn-gold btn-sm" onClick={() => navigate('/login')}>
              Provider Login
            </button>
          </div>
        </div>
      </nav>

     {/* HERO SECTION */}
      <section className={`hero ${isHeroVisible ? 'hero-visible' : ''}`}>
        <div className="hero-content">
          <h1 className="hero-title">Advancing Retinal Screening Through AI</h1>
          <p className="hero-subtitle" style={{ color: '#0F172A', fontWeight: 500 }}>
            Bringing cutting-edge computer vision technology to diabetic retinopathy detection,
            enabling early intervention and preventing vision loss in underserved communities.
          </p>
          <button className="btn btn-gold btn-lg hero-cta" onClick={() => navigate('/patient-lookup')}>
            Access Your Results
          </button>
        </div>
        <div className="hero-background" />
      </section>

      {/* VALUE PROPOSITION */}
      <section className="value-section container">
        <h2 className="section-title">How RetinalCare Works</h2>
        <div className="grid-3">
          <div
            className={`card card-interactive value-card ${visibleCards['value-1'] ? 'card-visible' : ''}`}
            data-section-id="value-1"
            ref={(el) => setRef('value-1', el)}
            onClick={() => setIsChatOpen(true)}
            style={{ cursor: 'pointer' }}
          >
            <div className="value-card-icon">🤖</div>
            <h3>AI-Assisted Screening</h3>
            <p>
              Advanced computer vision models assist healthcare workers in analyzing retinal images,
              providing consistent, objective grading to identify early signs of diabetic retinopathy.
            </p>
          </div>

          <div
            className={`card card-interactive value-card ${visibleCards['value-2'] ? 'card-visible' : ''}`}
            data-section-id="value-2"
            ref={(el) => setRef('value-2', el)}
          >
            <div className="value-card-icon">👨‍⚕️</div>
            <h3>Remote Specialist Review</h3>
            <p>
              Specialist ophthalmologists can review and validate AI assessments remotely,
              enabling expert care even in areas with limited access to eye care specialists.
            </p>
          </div>

          <div
            className={`card card-interactive value-card ${visibleCards['value-3'] ? 'card-visible' : ''}`}
            data-section-id="value-3"
            ref={(el) => setRef('value-3', el)}
          >
            <div className="value-card-icon">⚡</div>
            <h3>Faster Access to Care</h3>
            <p>
              Streamlined workflows prioritize high-risk patients for urgent review,
              ensuring rapid referral to treatment and reducing preventable vision loss.
            </p>
          </div>
        </div>
      </section>

      {/* EDUCATION SECTION */}
      <section id="education" className="education-section">
        <div className="container">
          <h2 className="section-title">Understanding Diabetic Retinopathy</h2>
          <p className="section-subtitle">
            Learn why early detection and screening matter for people living with diabetes
          </p>

          <div className="grid-3">
            <div
              className={`card card-interactive education-card ${visibleCards['edu-1'] ? 'card-visible' : ''}`}
              data-section-id="edu-1"
              ref={(el) => setRef('edu-1', el)}
            >
              <div className="education-card-header">
                <h4>Understanding Diabetic Retinopathy</h4>
              </div>
              <div className="education-card-body">
                <p>
                  Diabetic retinopathy (DR) is a leading cause of blindness among working-age adults worldwide.
                  It affects an estimated <strong>93 million people</strong> globally, yet early detection can prevent
                  vision loss in most cases. DR occurs when high blood sugar levels damage the tiny blood vessels in the retina.
                </p>
              </div>
            </div>

            <div
              className={`card card-interactive education-card ${visibleCards['edu-2'] ? 'card-visible' : ''}`}
              data-section-id="edu-2"
              ref={(el) => setRef('edu-2', el)}
            >
              <div className="education-card-header">
                <h4>Why Early Screening Matters</h4>
              </div>
              <div className="education-card-body">
                <p>
                  DR often shows <strong>no symptoms in its early stages</strong>, which is why regular retinal screening
                  is critical for anyone living with diabetes. In regions with limited access to ophthalmologists,
                  screening can be challenging. RetinalCare brings screening closer to patients through AI-assisted analysis.
                </p>
              </div>
            </div>

            <div
              className={`card card-interactive education-card ${visibleCards['edu-3'] ? 'card-visible' : ''}`}
              data-section-id="edu-3"
              ref={(el) => setRef('edu-3', el)}
            >
              <div className="education-card-header">
                <h4>AI-Assisted Detection</h4>
              </div>
              <div className="education-card-body">
                <p>
                  Modern computer vision models can assist healthcare workers in grading retinal images for signs of DR,
                  helping prioritize which patients need urgent specialist review. This technology augments,
                  not replaces, clinical judgment and expertise.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="cta-section">
        <div className="container container-sm">
          <h2>Ready to Get Started?</h2>
          <p>
            If you were screened and received a Patient ID, access your results securely.
            Healthcare providers can log in to review and manage patient assessments.
          </p>
          <div className="cta-buttons">
            <button className="btn btn-gold btn-lg" onClick={() => navigate('/patient-lookup')}>
              Patient Portal
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => navigate('/login')}>
              Provider Login
            </button>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>RetinalCare</h4>
              <p className="footer-mission">
                Advancing retinal health through AI-assisted screening, bringing expert care
                to underserved communities and enabling early intervention to prevent vision loss.
              </p>
            </div>
            <div className="footer-section">
              <h5>Quick Links</h5>
              <ul>
                <li><a href="#about">About</a></li>
                <li><a href="/#features">Features</a></li>
                <li><a href="/#education">Education</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h5>For Everyone</h5>
              <ul>
                <li><a href="/patient-lookup">Patient Portal</a></li>
                <li><a href="/login">Provider Login</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2026 RetinalCare. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

