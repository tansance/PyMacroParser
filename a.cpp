#ifndef MCTEST
#define MCTEST

#ifdef MC1

#define data1 0x20
/*cmment start*/#define /*this is comment*/ data2 2.5f
#define data3 L"this is a \"data"
#define data4 true


#ifdef MC2

#define data5 'a'
#define data6 { {2.0, "abc"}, {1.5, "def"}, {5.6f, "7.2"}} // 浮点与字符串组成的结构体初始化聚合， 再进一步聚合组成了数组

#else

#define data5 {5.0, 7.5, 3.8}
#define data6 'c'

#endif //end MC2


#else

#define data1 1.0f /* this is float
may be changed
*/
#define data2 2
#define data3 false
#define data4 "this is a data"


#ifdef MC2

#define data5 'B'
#define data6 {1, 6, 3}
#define data7 0xa

#else

#define data5 'D'
#define data6 {1, 6}

#endif //end MC2

#endif //MC1

#ifdef MC2
#undef MC2
#endif

#endif // !MC_TEST