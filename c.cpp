#ifndef MC_TEST
#define MC_TEST
#define WIDTH  123.0//number
#define HEIGHT  123 //int number
#ifdef MAC1
	#undef MAC1
	#define XF 2.3e6
	#ifdef MAC2
	#undef HEIGHT
	#define HEIGHT 1e6
	#ifdef MAC1
	#define XF2  -2         /* name used but not defined in nested block */
	#else
	#endif //!MAC1 again
	#ifndef MAC3
	#define MAC3 "mac13"
	#define XF3 true
	#else
	#endif //!MAC3
	#else
	//redefine WIDTH!
	#undef WIDTH
	#define WIDTH 100
	//to define MAC2:
	#define MAC2 "mac12"
	#endif  //!MAC2
#else
	#define MAC1 "mac1"
	#define XF -1.2e8
/*mac2*/#ifdef MAC2
	#ifdef MAC1
	#define XF2  3
	#else
	#define XF2  4
	#endif //!MAC1 again
	#ifndef MAC3
	#define MAC3 "mac03"
	#define XF3 "ok"
	#else
	#endif //!MAC3
	#else
	#undef WIDTH
	#define WIDTH 98.1
	//to define MAC2:
	#define MAC2 "mac02"
	#ifdef MAC3
	#define XF3 "unok"
	#endif
	#endif
	#define PLATFORM64
#endif  //!MAC1
#ifdef MAC1
#define TestMac1 "TestMac exist"
#else
#define TestMac1 "TestMac not exist"
#endif
# /*If*/ ifdef PLATFORM64
	/* On a 64-bit system, rename the MyInit */
	#define MyInit "MyInit_64"
# else
	#define MyInit "MyInit"
# /*End*/ endif
 ///line comment
#ifdef TRACE_REFS
 /* When we are tracing reference counts,
 rename MyInit */
# undef MyInit
#ifdef PLATFORM64
	#define MyInit "MyInitTraceRefs_64"
#else
	#define MyInit "MyInitTraceRefs"
#endif
#endif
#define TRACE_REFS
#else
#endif // !MC_TEST