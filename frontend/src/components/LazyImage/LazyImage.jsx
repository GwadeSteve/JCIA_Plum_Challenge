import React, { useState, useEffect } from 'react';

const LazyImage = ({ src, alt, placeholder, ...props }) => {
  const [imageSrc, setImageSrc] = useState(placeholder || '');
  const [imageRef, setImageRef] = useState();

  useEffect(() => {
    let observer;
    let didCancel = false;

    if (imageRef && imageSrc === placeholder) {
      observer = new IntersectionObserver(
        entries => {
          entries.forEach(entry => {
            if (
              !didCancel &&
              (entry.intersectionRatio > 0 || entry.isIntersecting)
            ) {
              import(`${src}`).then(image => {
                setImageSrc(image.default);
              }).catch(() => {
                setImageSrc(src);
              });
              
              observer.unobserve(imageRef);
            }
          });
        },
        {
          threshold: 0.01,
          rootMargin: '75%'
        }
      );
      observer.observe(imageRef);
    }
    return () => {
      didCancel = true;
      if (observer && imageRef) {
        observer.unobserve(imageRef);
      }
    };
  }, [imageRef, imageSrc, placeholder, src]);

  return (
    <img
      ref={setImageRef}
      src={imageSrc}
      alt={alt}
      {...props}
      style={{ 
        ...props.style,
        transition: 'opacity 0.5s',
        opacity: imageSrc === placeholder ? 0.5 : 1
      }}
    />
  );
};

export default LazyImage;