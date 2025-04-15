import React, { useState } from "react";
import "./TeamPage.css";

const teamMembers = [
  {
    name: "Samy junior",
    role: "Entrainer les model",
    description:
      "Responsable de la modélisation IA pour la classification des prunes.",
    photo: "/images/S.png",
  },
  {
    name: "Avodagbe Ze Paul",
    role: "Développeur Full Stack",
    description:
      "A conçu l’interface web et a intégré le modèle IA dans le système.",
    photo: "/images/A.png",
  },
  {
    name: "Gwade Steve ",
    role: "Chef de projet",
    description:
      "Coordination du projet et lien avec les acteurs du domaine agricole.",
    photo: "/images/P.png",
  },
  {
    name: "Njimeyup Harold",
    role: "DevOps & Intégrateur",
    description:
      "Mise en place de l’environnement cloud pour les tests en conditions réelles.",
    photo: "/images/H.png",
  },
  {
    name: "Murielle",
    role: "Analyse des donnees",
    description: "Preparer les donnees pour l'entrainement.",
    photo: "/images/P.png",
  },
];

const TeamPage = () => {
  const [selected, setSelected] = useState(null);

  return (
    <div className={`team-page ${selected ? "blurred" : ""}`}>
      <section className="intro-text">
        <h2>Un projet au service de l'agriculture locale</h2>
        <p>
          Dans un contexte où la qualité des prunes africaines est essentielle
          pour les marchés locaux et internationaux, notre équipe a développé
          une solution intelligente capable d'automatiser le tri des fruits. Ce
          projet vise à aider les producteurs à gagner du temps, réduire les
          pertes et garantir une meilleure rentabilité.
        </p>
      </section>

      <h1 className="title">Notre Équipe</h1>

      <div className="carousel-container">
        <div className="carousel-track">
          {teamMembers.map((member, index) => (
            <div
              className="team-card"
              key={index}
              onClick={() => setSelected(member)}
            >
              <img
                src={member.photo}
                alt={member.name}
                className="team-photo"
              />
              <h3>{member.name}</h3>
              <p className="role">{member.role}</p>
              <p className="desc">{member.description}</p>
            </div>
          ))}
        </div>
      </div>

      <section className="outro-text">
        <h2>Et après ?</h2>
        <p>
          Ce prototype n'est qu'une première étape. À l'avenir, nous envisageons
          d'intégrer des capteurs physiques, d'élargir le modèle à d'autres
          fruits locaux et de proposer une solution complète à destination des
          coopératives agricoles. Grâce au soutien du JCIA Hackathon, nous
          espérons poser les bases d'une transformation digitale de la filière
          prune.
        </p>
      </section>

      {/* === MODALE EN GRAND === */}
      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <img src={selected.photo} alt={selected.name} />
            <h2>{selected.name}</h2>
            <h4>{selected.role}</h4>
            <p>{selected.description}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamPage;
