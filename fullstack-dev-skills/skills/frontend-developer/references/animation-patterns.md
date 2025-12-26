# Animation Patterns Reference

Production-ready animation recipes for React applications using Motion (Framer Motion).

## Table of Contents
1. [Page Transitions](#page-transitions)
2. [Scroll Animations](#scroll-animations)
3. [Gesture Interactions](#gesture-interactions)
4. [List & Stagger Effects](#list--stagger-effects)
5. [Layout Animations](#layout-animations)
6. [Loading States](#loading-states)
7. [Micro-interactions](#micro-interactions)
8. [Statement Pieces](#statement-pieces)

## Page Transitions

### Fade Slide
```tsx
import { motion, AnimatePresence } from "motion/react";

const PageTransition = ({ children, key }) => (
  <AnimatePresence mode="wait">
    <motion.div
      key={key}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      {children}
    </motion.div>
  </AnimatePresence>
);
```

### Shared Layout Transition
```tsx
const SharedLayoutPage = ({ id, children }) => (
  <motion.div
    layoutId={`page-${id}`}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
  >
    {children}
  </motion.div>
);
```

### Clip Path Reveal
```tsx
const ClipReveal = ({ children }) => (
  <motion.div
    initial={{ clipPath: "inset(0 100% 0 0)" }}
    animate={{ clipPath: "inset(0 0% 0 0)" }}
    exit={{ clipPath: "inset(0 0 0 100%)" }}
    transition={{ duration: 0.6, ease: [0.65, 0, 0.35, 1] }}
  >
    {children}
  </motion.div>
);
```

## Scroll Animations

### Fade In on Scroll
```tsx
const FadeInOnScroll = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 50 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-100px" }}
    transition={{ duration: 0.6, ease: "easeOut" }}
  >
    {children}
  </motion.div>
);
```

### Parallax Effect
```tsx
import { useScroll, useTransform, motion } from "motion/react";
import { useRef } from "react";

const Parallax = ({ children, offset = 50 }) => {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });
  
  const y = useTransform(scrollYProgress, [0, 1], [offset, -offset]);
  
  return (
    <motion.div ref={ref} style={{ y }}>
      {children}
    </motion.div>
  );
};
```

### Progress Indicator
```tsx
const ScrollProgress = () => {
  const { scrollYProgress } = useScroll();
  
  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-1 bg-primary origin-left"
      style={{ scaleX: scrollYProgress }}
    />
  );
};
```

### Reveal on Scroll (Multiple Directions)
```tsx
const directions = {
  up: { initial: { y: 50 }, animate: { y: 0 } },
  down: { initial: { y: -50 }, animate: { y: 0 } },
  left: { initial: { x: 50 }, animate: { x: 0 } },
  right: { initial: { x: -50 }, animate: { x: 0 } },
};

const RevealOnScroll = ({ children, direction = "up" }) => (
  <motion.div
    initial={{ opacity: 0, ...directions[direction].initial }}
    whileInView={{ opacity: 1, ...directions[direction].animate }}
    viewport={{ once: true }}
    transition={{ duration: 0.5, ease: "easeOut" }}
  >
    {children}
  </motion.div>
);
```

## Gesture Interactions

### Magnetic Button
```tsx
import { useMotionValue, useSpring, motion } from "motion/react";
import { useRef } from "react";

const MagneticButton = ({ children }) => {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const springX = useSpring(x, { stiffness: 300, damping: 30 });
  const springY = useSpring(y, { stiffness: 300, damping: 30 });
  
  const handleMouseMove = (e) => {
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set((e.clientX - centerX) * 0.3);
    y.set((e.clientY - centerY) * 0.3);
  };
  
  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };
  
  return (
    <motion.button
      ref={ref}
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.button>
  );
};
```

### Draggable Card
```tsx
const DraggableCard = ({ children }) => (
  <motion.div
    drag
    dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
    dragElastic={0.1}
    whileDrag={{ scale: 1.05, cursor: "grabbing" }}
    whileHover={{ cursor: "grab" }}
    className="select-none"
  >
    {children}
  </motion.div>
);
```

### Swipe to Dismiss
```tsx
const SwipeToDismiss = ({ onDismiss, children }) => (
  <motion.div
    drag="x"
    dragConstraints={{ left: 0, right: 0 }}
    onDragEnd={(_, info) => {
      if (Math.abs(info.offset.x) > 100) {
        onDismiss();
      }
    }}
  >
    {children}
  </motion.div>
);
```

## List & Stagger Effects

### Staggered List
```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

const StaggeredList = ({ items }) => (
  <motion.ul variants={container} initial="hidden" animate="show">
    {items.map((item, i) => (
      <motion.li key={i} variants={item}>
        {item}
      </motion.li>
    ))}
  </motion.ul>
);
```

### Animate Presence List
```tsx
const AnimatedList = ({ items }) => (
  <AnimatePresence mode="popLayout">
    {items.map((item) => (
      <motion.div
        key={item.id}
        layout
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.8 }}
        transition={{ type: "spring", stiffness: 300, damping: 25 }}
      >
        {item.content}
      </motion.div>
    ))}
  </AnimatePresence>
);
```

### Grid Stagger
```tsx
const GridStagger = ({ children }) => {
  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.05,
        staggerDirection: 1,
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { type: "spring", stiffness: 400, damping: 25 }
    }
  };
  
  return (
    <motion.div
      className="grid grid-cols-3 gap-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {React.Children.map(children, (child) => (
        <motion.div variants={itemVariants}>{child}</motion.div>
      ))}
    </motion.div>
  );
};
```

## Layout Animations

### Expanding Card
```tsx
const ExpandingCard = ({ id, isOpen, children, preview }) => (
  <>
    <motion.div
      layoutId={`card-${id}`}
      onClick={() => !isOpen && setOpen(id)}
      className="cursor-pointer"
    >
      <motion.div layoutId={`card-content-${id}`}>
        {preview}
      </motion.div>
    </motion.div>
    
    <AnimatePresence>
      {isOpen && (
        <motion.div
          layoutId={`card-${id}`}
          className="fixed inset-4 z-50"
        >
          <motion.div layoutId={`card-content-${id}`}>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  </>
);
```

### Tab Content Switch
```tsx
const TabContent = ({ activeTab, tabs }) => (
  <AnimatePresence mode="wait">
    <motion.div
      key={activeTab}
      initial={{ opacity: 0, x: 10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -10 }}
      transition={{ duration: 0.2 }}
    >
      {tabs[activeTab]}
    </motion.div>
  </AnimatePresence>
);
```

### Accordion
```tsx
const Accordion = ({ isOpen, children }) => (
  <AnimatePresence initial={false}>
    {isOpen && (
      <motion.div
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: "auto", opacity: 1 }}
        exit={{ height: 0, opacity: 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        style={{ overflow: "hidden" }}
      >
        {children}
      </motion.div>
    )}
  </AnimatePresence>
);
```

## Loading States

### Skeleton Shimmer
```tsx
const Skeleton = ({ className }) => (
  <motion.div
    className={`bg-muted ${className}`}
    animate={{
      backgroundPosition: ["200% 0", "-200% 0"],
    }}
    transition={{
      duration: 1.5,
      repeat: Infinity,
      ease: "linear",
    }}
    style={{
      backgroundImage: 
        "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%)",
      backgroundSize: "200% 100%",
    }}
  />
);
```

### Spinner
```tsx
const Spinner = ({ size = 24 }) => (
  <motion.div
    className="border-2 border-muted border-t-primary rounded-full"
    style={{ width: size, height: size }}
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
  />
);
```

### Dots Loader
```tsx
const DotsLoader = () => (
  <motion.div className="flex gap-1">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="w-2 h-2 bg-primary rounded-full"
        animate={{ y: [0, -8, 0] }}
        transition={{
          duration: 0.6,
          repeat: Infinity,
          delay: i * 0.1,
        }}
      />
    ))}
  </motion.div>
);
```

## Micro-interactions

### Button Press
```tsx
const PressButton = ({ children, ...props }) => (
  <motion.button
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    transition={{ type: "spring", stiffness: 400, damping: 17 }}
    {...props}
  >
    {children}
  </motion.button>
);
```

### Checkbox
```tsx
const AnimatedCheckbox = ({ checked, onChange }) => (
  <motion.button
    onClick={onChange}
    className="w-6 h-6 border-2 rounded flex items-center justify-center"
    animate={{
      backgroundColor: checked ? "var(--color-primary)" : "transparent",
      borderColor: checked ? "var(--color-primary)" : "var(--color-muted)",
    }}
  >
    <motion.svg
      viewBox="0 0 24 24"
      className="w-4 h-4"
      initial={false}
      animate={{ pathLength: checked ? 1 : 0 }}
    >
      <motion.path
        d="M5 12l5 5L20 7"
        fill="none"
        stroke="white"
        strokeWidth={3}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </motion.svg>
  </motion.button>
);
```

### Toggle Switch
```tsx
const Toggle = ({ isOn, onToggle }) => (
  <motion.button
    onClick={onToggle}
    className="w-14 h-8 rounded-full p-1"
    animate={{ backgroundColor: isOn ? "var(--color-primary)" : "var(--color-muted)" }}
  >
    <motion.div
      className="w-6 h-6 bg-white rounded-full"
      animate={{ x: isOn ? 22 : 0 }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
    />
  </motion.button>
);
```

### Ripple Effect
```tsx
const RippleButton = ({ children }) => {
  const [ripples, setRipples] = useState([]);
  
  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ripple = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      id: Date.now(),
    };
    setRipples((prev) => [...prev, ripple]);
  };
  
  return (
    <button className="relative overflow-hidden" onClick={handleClick}>
      {children}
      {ripples.map((ripple) => (
        <motion.span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full pointer-events-none"
          style={{ left: ripple.x, top: ripple.y, x: "-50%", y: "-50%" }}
          initial={{ width: 0, height: 0, opacity: 0.5 }}
          animate={{ width: 500, height: 500, opacity: 0 }}
          transition={{ duration: 0.6 }}
          onAnimationComplete={() => 
            setRipples((prev) => prev.filter((r) => r.id !== ripple.id))
          }
        />
      ))}
    </button>
  );
};
```

## Statement Pieces

### Text Reveal
```tsx
const TextReveal = ({ text }) => {
  const words = text.split(" ");
  
  return (
    <motion.p
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
    >
      {words.map((word, i) => (
        <motion.span
          key={i}
          className="inline-block mr-2"
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: {
              opacity: 1,
              y: 0,
              transition: { delay: i * 0.05 },
            },
          }}
        >
          {word}
        </motion.span>
      ))}
    </motion.p>
  );
};
```

### Cursor Follower
```tsx
const CursorFollower = () => {
  const cursorX = useMotionValue(0);
  const cursorY = useMotionValue(0);
  
  const springX = useSpring(cursorX, { stiffness: 500, damping: 28 });
  const springY = useSpring(cursorY, { stiffness: 500, damping: 28 });
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      cursorX.set(e.clientX - 16);
      cursorY.set(e.clientY - 16);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);
  
  return (
    <motion.div
      className="fixed w-8 h-8 rounded-full bg-primary/30 pointer-events-none z-50 mix-blend-difference"
      style={{ x: springX, y: springY }}
    />
  );
};
```

### Infinite Marquee
```tsx
const Marquee = ({ children, speed = 20 }) => (
  <div className="overflow-hidden">
    <motion.div
      className="flex whitespace-nowrap"
      animate={{ x: [0, "-50%"] }}
      transition={{
        x: { duration: speed, repeat: Infinity, ease: "linear" },
      }}
    >
      {children}
      {children}
    </motion.div>
  </div>
);
```

## Spring Presets

```tsx
const springs = {
  // Snappy, responsive feel
  snappy: { type: "spring", stiffness: 400, damping: 25 },
  
  // Smooth, elegant motion
  smooth: { type: "spring", stiffness: 200, damping: 20 },
  
  // Bouncy, playful feel
  bouncy: { type: "spring", stiffness: 300, damping: 10 },
  
  // Slow, dramatic reveal
  dramatic: { type: "spring", stiffness: 100, damping: 15 },
  
  // Quick micro-interaction
  micro: { type: "spring", stiffness: 500, damping: 30 },
};
```

## Easing Functions

```tsx
const easings = {
  // Standard eases
  easeOut: [0, 0, 0.2, 1],
  easeIn: [0.4, 0, 1, 1],
  easeInOut: [0.4, 0, 0.2, 1],
  
  // Expressive eases
  anticipate: [0.36, 0, 0.66, -0.56],
  overshoot: [0.34, 1.56, 0.64, 1],
  
  // Dramatic eases
  dramatic: [0.65, 0, 0.35, 1],
  elastic: [0.68, -0.55, 0.265, 1.55],
};
```
