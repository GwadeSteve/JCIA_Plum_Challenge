import React from 'react';
import './PropositionTeamPage.css';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';
import { HiOutlineCode, HiOutlineDatabase, HiOutlineChartBar, 
         HiOutlineDesktopComputer, HiOutlineLightBulb, HiOutlineStar,
         HiOutlineAcademicCap, HiOutlineGlobe } from 'react-icons/hi';
import { BsGraphUp, BsShieldCheck, BsLightningCharge } from 'react-icons/bs';
import { MdOutlineSignalWifiOff, MdOutlinePhoneAndroid, MdOutlineAccessTime } from 'react-icons/md';
import gwadeImage from "../../assets/team/Gwade Steve 2.jpg"
import avodaImage from "../../assets/team/Valery.jpg"
import haroldImage from "../../assets/team/Harold Njimeyup.jpg"
import mureilleImage from "../../assets/team/Murielle Sharane.jpg"
import samyImage from "../../assets/team/Mintyene.jpg"
import farmerImage from "../../assets/team/Farmer.png"

const PropositionTeamPage = () => {
  const teamMembers = [
    {
      name: "Gwade Steve Vaelle",
      roles: ["Team Lead", "Deep Learning", "Backend Developer"],
      bio: "Currently a Data Science and Artificial Intelligence Research Student at ENSPD, I aspire to become a Computer Vision Researcher. I've always been fascinated about how algorithms learn and how AI can solve real african challenges from healthcare to agriculture.",
      image: gwadeImage,
      socials: {
        github: "https://github.com/GwadeSteve",
        linkedin: "https://www.linkedin.com/in/gwade-steve-0414b8249?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app",
        twitter: "https://x.com/SteveGwade?t=0TjmjV0VPJ8EmMiNKOoemg&s=09"
      },
      roleIcons: [<HiOutlineStar key="star" />, <HiOutlineLightBulb key="dl" />, <HiOutlineDatabase key="backend" />]
    },
    {
      name: "Avodagbe Ze Paul Valery",
      roles: ["Frontend Developer", "Deep Learning"],
      bio: "I'm passionate about creating AI that truly understands the world. At ENSPD, I explore how intelligent systems can solve real problems and I believe technology should be inclusive, relevant, and human-centered. My goal is to make AI more impactful for our communities.",
      image: avodaImage,
      socials: {
        github: "https://github.com/cookie-pii",
        linkedin: "https://linkedin.com/in/avodagbe-ze-paul-valery-5636a826a",
      },
      roleIcons: [
        <HiOutlineCode key="frontend" />,
        <HiOutlineLightBulb key="dl" />,
      ],
    },
    {
      name: "Njimeyup Mbouombouo Harold Francois",
      roles: ["Research", "Deep Learning", 'Frontend Developer',"UI/UX"],
      bio: "Passionate about tomorrow’s technologies with a strong focus on functional and thoughtful design, I believe technology truly shines when it’s intuitive, elegant, and accessible. Curious, creative, and driven by purpose, I strive to develop meaningful projects that place the user at the heart of innovation.",
      image: haroldImage,
      socials: {
        github: "https://github.com/HaroldNjimeyup",
        linkedin: "https://www.linkedin.com/in/harold-njimeyup-906a20297?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app",
        twitter: "https://twitter.com/NHarold_pro"
      },
      roleIcons: [<HiOutlineAcademicCap key="research" />, <HiOutlineLightBulb key="dl" />, <HiOutlineCode key="frontend" />]
    },
    {
      name: "Magne Mureille Sharane",
      roles: ["Data Scientist", "Database"],
      bio: "My name is Mureille Sharane Magne, a Master's student in Data Science and Artificial Intelligence at ENSPD. I define myself as a curious and hardworking woman, passionate about what I do and not afraid to take on new challenges.",
      image: mureilleImage,
      socials: {
        github: "https://github.com/Mureille-Ma",
        linkedin: "https://www.linkedin.com/in/mureille-signe-089a35328?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app"
      },
      roleIcons: [<HiOutlineChartBar key="data" />, <HiOutlineDatabase key="db" />]
    },
    {
      name: "Mintyene Samy Junior",
      roles: ["Computer Vision", "Backend Developer"],
      bio: "I'm passionate about harnessing AI, particularly image recognition, to tackle real-world challenges. By focusing on practical solutions, I hope to make a meaningful difference through technology.",
      image: samyImage,
      socials: {
        github: "https://github.com/M1nty3n3",
        linkedin: "https://www.linkedin.com/in/samy-mintyene-602894311?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app"
      },
      roleIcons: [<HiOutlineDesktopComputer key="cv" />, <HiOutlineDatabase key="backend" />]
    }
  ];

  const missionStatement = {
    title: "Our Mission",
    text: "As ENSPD students who've seen firsthand how post-harvest losses affect our communities, we're creating a bridge between traditional knowledge and cutting-edge AI. Our solution isn't imported from elsewhere; it's built for Cameroon's unique challenges, by Cameroonians who understand the problem from the inside.",
    goals: [
      "Cut post-harvest losses nearly in half for smallholder farmers who can't afford complex equipment",
      "Create technology that works in the real world - spotty internet, dusty conditions, and all",
      "Put the power of AI into the hands of 500+ local farmers who've never used technology in their work",
      "Build a solution specifically calibrated for Cameroonian safou varieties that global models often misclassify"
    ]
  };

  const impactStats = [
    {
      number: "76%",
      description: "of small-scale farmers report significant income loss due to quality misjudgments",
      icon: <BsGraphUp size={30} />
    },
    {
      number: "40%",
      description: "reduction in waste when farmers can accurately assess plum quality",
      icon: <BsShieldCheck size={30} />,
      highlight: true
    },
    {
      number: "8000+",
      description: "families across Western Cameroon depend on safou cultivation for livelihood",
      icon: <HiOutlineGlobe size={30} />
    }
  ];

  return (
    <div className="proposition-team-page">
      <section className="team-header" data-aos="fade-up">
        <h1 className="xxl-font gradient-text">Meet Our Team</h1>
        <p className="m-font">Five students from ENSPD with one mission: revolutionizing plum quality assessment</p>
      </section>

      <section className="mission-section">
        <div className="mission-content">
          <h2 className="xl-font gradient-text">{missionStatement.title}</h2>
          <p className="s-font">{missionStatement.text}</p>
          
          <div className="goals-container" data-aos="fade-left">
            <h3 className="l-font">What We're Building for JCIA</h3>
            <ul className="goals-list">
              {missionStatement.goals.map((goal, index) => (
                <li key={index} className="goal-item s-font">
                  <span className="goal-marker">✦</span>
                  {goal}
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="mission-image" data-aos="fade-right">
          <img src="https://th.bing.com/th/id/R.6c91ee0b39134bc953d6d9991ba03295?rik=sqCaC%2bhvZNIxhw&riu=http%3a%2f%2fsymbolhunt.com%2fwp-content%2fuploads%2f2020%2f12%2fSafou.jpg&ehk=SX1zgcdcJoyaVB5O4HjsD3Gr76U0gaz6ls8TlCEV%2fDM%3d&risl=&pid=ImgRaw&r=0" alt="Safou Market in Cameroon" />
          <div className="image-overlay">
            <span className="xl-font">PlumVision</span>
          </div>
        </div>
      </section>

      <section className="team-grid" data-aos="fade-up">
        {teamMembers.map((member, index) => (
          <div className="team-card" key={index} data-aos="fade-in">
            <div className="member-image-container">
              <img src={member.image} alt={member.name} />
              <div className="image-overlay-gradient"></div>
              <div className="role-icons">
                {member.roleIcons.map((icon, iconIndex) => (
                  <div 
                    className={`role-icon ${member.roles[iconIndex] === 'Team Lead' ? 'leader-icon' : ''}`} 
                    key={iconIndex}
                    title={member.roles[iconIndex]}
                  >
                    {icon}
                  </div>
                ))}
              </div>
            </div>
            <div className="member-info">
              <h3 className="m-font">{member.name}</h3>
              <div className="member-roles">
                {member.roles.map((role, roleIndex) => (
                  <span key={roleIndex} className={`role-tag ${role === 'Team Lead' ? 'leader-tag' : ''}`}>
                    {role}
                  </span>
                ))}
              </div>
              <p className="member-bio s-font">{member.bio}</p>
              <div className="social-links">
                {member.socials.github && (
                  <a href={member.socials.github} target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                    <FaGithub />
                  </a>
                )}
                {member.socials.linkedin && (
                  <a href={member.socials.linkedin} target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                    <FaLinkedin />
                  </a>
                )}
                {member.socials.twitter && (
                  <a href={member.socials.twitter} target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                    <FaTwitter />
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </section>

      <section className="community-impact">
        <h2 className="xl-font gradient-text" data-aos="fade-down" data-aos-duration="300">Real Impact for Cameroon</h2>
        
        <div className="impact-intro">
          <p className="l-font" data-aos="fade-up" data-aos-duration="300">
            For most Cameroonians, safou isn't just food – it's economic security. Our technology builds on centuries of traditional knowledge, bringing new precision to quality assessment that could transform thousands of livelihoods.
          </p>
        </div>
        
        <div className="impact-stats-grid">
          {impactStats.map((stat, index) => (
            <div 
              key={index} 
              className={`impact-stat-card ${stat.highlight ? 'highlight' : ''}`}
            >
              <div className="stat-icon">
                {stat.icon}
              </div>
              <div className="stat-content">
                <span className="stat-number">{stat.number}</span>
                <span className="stat-description">{stat.description}</span>
              </div>
            </div>
          ))}
        </div>
        
        <div className="impact-visual-section">
          <div className="impact-visual-content">
            <h3 className="l-font">Technology That Makes Sense Here</h3>
            <p className="m-font">
              Understanding farmers and enterprises challenges before writing a single line of code was key. Our solution is not only technically sound, it's relevant and useful for the people who need it most.
            </p>
            <div className="impact-features">
              <div className="impact-feature" data-aos="fade-left" data-aos-duration="300">
                <div className="feature-icon">
                  <MdOutlineSignalWifiOff />
                </div>
                <div className="feature-text">
                  <h4>Available Offline</h4>
                  <p>PlumVision can function without internet access</p>
                </div>
              </div>
              <div className="impact-feature" data-aos="fade-left" data-aos-duration="350">
                <div className="feature-icon">
                  <BsLightningCharge />
                </div>
                <div className="feature-text">
                  <h4>Real-time Analysis</h4>
                  <p>Obtain results in seconds, and keep pace with busy days</p>
                </div>
              </div>
              <div className="impact-feature" data-aos="fade-left" data-aos-duration="400">
                <div className="feature-icon">
                  <MdOutlinePhoneAndroid />
                </div>
                <div className="feature-text">
                  <h4>Performance Beast</h4>
                  <p>Optimized for the devices farmers already own</p>
                </div>
              </div>
              <div className="impact-feature" data-aos="fade-left" data-aos-duration="450">
                <div className="feature-icon">
                  <MdOutlineAccessTime />
                </div>
                <div className="feature-text">
                  <h4>Learns Over Time</h4>
                  <p>Our model improves over time, adapting to changing conditions</p>
                </div>
              </div>
            </div>
          </div>
          <div className="impact-visual-image">
            <img src={farmerImage} alt="Cameroon farmer using PlumVision" />
          </div>
        </div>
      </section>

        <section className="call-to-action">
            <div className="cta-content">
                <h2 className="xl-font gradient-text">Ready to see our solution in action?</h2>
                <p className="m-font">Explore our demo to experience how PlumVision can transform quality assessment across Cameroon.</p>
                <button className="filled-violet cta-button" onClick={() => window.location.href = '/demo'}>
                <HiOutlineDesktopComputer size={20} />
                <span>Try the Demo</span>
                </button>
            </div>
            <div className="cta-decoration">
                <div className="cta-circle circle-1"></div>
                <div className="cta-circle circle-2"></div>
                <div className="cta-circle circle-3"></div>
            </div>
        </section>
    </div>
  );
};

export default PropositionTeamPage;