source_filename = "/home/tijl/code/llmO/SUT/top_words_from_file.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"
%M = type { ptr, ptr, i64 }
%W = type { ptr, i64 }
%I = type { ptr, i64, i64 }
@.str = private constant [3 x i8] c"rb\00"
define ptr @top_words_from_file(ptr %0, ptr %1, i64 %2, i64 %3, ptr %4) {
%6 = alloca ptr
%7 = alloca i64
%8 = alloca %M
%9 = alloca i64
%10 = icmp eq ptr %4, null
br i1 %10, label %12, label %11
11:
store i64 0, ptr %4
br label %12
12:
%13 = icmp eq ptr %0, null
br i1 %13, label %139, label %14
14:
%15 = icmp eq ptr %1, null
%16 = icmp ne i64 %2, 0
%17 = and i1 %15, %16
br i1 %17, label %139, label %18
18:
store ptr null, ptr %6
store i64 0, ptr %7
call void @llvm.memset.p0.i64(ptr %8, i8 0, i64 24, i1 false)
store i64 0, ptr %9
%19 = call i32 @a(ptr %1, i64 %2, ptr %6, ptr %7)
%20 = icmp eq i32 %19, 0
br i1 %20, label %132, label %21
21:
%22 = call ptr @b(ptr %0, ptr %9)
%23 = icmp eq ptr %22, null
br i1 %23, label %132, label %24
24:
%25 = call i32 @c(ptr %8)
%26 = icmp eq i32 %25, 0
br i1 %26, label %132, label %27
27:
%28 = load i64, ptr %9
%29 = load ptr, ptr %6
%30 = load i64, ptr %7
br label %31
31:
%32 = phi i64 [ %62, %58 ], [ 0, %27 ]
%33 = phi i32 [ %59, %58 ], [ 0, %27 ]
%34 = phi i64 [ %60, %58 ], [ 0, %27 ]
%35 = phi i64 [ %61, %58 ], [ 0, %27 ]
%36 = icmp eq i64 %32, %28
br i1 %36, label %63, label %37
37:
%38 = getelementptr i8, ptr %22, i64 %32
%39 = load i8, ptr %38
%40 = call zeroext i1 @_Z12is_word_charc(i8 signext %39)
%41 = icmp eq i32 %33, 0
br i1 %40, label %42, label %48
42:
%43 = select i1 %41, i64 %32, i64 %34
%44 = select i1 %41, i64 %32, i64 %35
%45 = call signext i8 @_Z14normalize_charc(i8 signext %39)
%46 = add i64 %43, 1
%47 = getelementptr i8, ptr %22, i64 %43
store i8 %45, ptr %47
br label %58
48:
br i1 %41, label %58, label %49
49:
%50 = sub i64 %34, %35
%51 = getelementptr i8, ptr %22, i64 %35
%52 = call i64 @d(ptr %51, i64 %50)
%53 = call i32 @e(ptr %29, i64 %30, ptr %51, i64 %50, i64 %52)
%54 = icmp eq i32 %53, 0
br i1 %54, label %55, label %58
55:
%56 = call i32 @f(ptr %8, ptr %51, i64 %50, i64 %52)
%57 = icmp eq i32 %56, 0
br i1 %57, label %132, label %58
58:
%59 = phi i32 [ 0, %48 ], [ 1, %42 ], [ 0, %49 ], [ 0, %55 ]
%60 = phi i64 [ %34, %48 ], [ %46, %42 ], [ %34, %49 ], [ %34, %55 ]
%61 = phi i64 [ %35, %48 ], [ %44, %42 ], [ %35, %49 ], [ %35, %55 ]
%62 = add i64 %32, 1
br label %31
63:
%64 = icmp eq i32 %33, 0
br i1 %64, label %74, label %65
65:
%66 = sub i64 %34, %35
%67 = getelementptr i8, ptr %22, i64 %35
%68 = call i64 @d(ptr %67, i64 %66)
%69 = call i32 @e(ptr %29, i64 %30, ptr %67, i64 %66, i64 %68)
%70 = icmp eq i32 %69, 0
br i1 %70, label %71, label %74
71:
%72 = call i32 @f(ptr %8, ptr %67, i64 %66, i64 %68)
%73 = icmp eq i32 %72, 0
br i1 %73, label %132, label %74
74:
%75 = getelementptr i8, ptr %8, i64 16
%76 = load i64, ptr %75
%77 = call i64 @llvm.umin.i64(i64 %76, i64 %3)
%78 = icmp eq i64 %77, 0
br i1 %78, label %79, label %80
79:
call void @g(ptr %8)
call void @free(ptr %22)
call void @h(ptr %29, i64 %30)
br label %137
80:
%81 = icmp ugt i64 %76, 2305843009213693951
br i1 %81, label %132, label %82
82:
%83 = shl i64 %76, 3
%84 = call ptr @malloc(i64 %83)
%85 = icmp eq ptr %84, null
br i1 %85, label %132, label %86
86:
%87 = phi ptr [ %90, %95 ], [ %8, %82 ]
%88 = phi i64 [ %96, %95 ], [ 0, %82 ]
%89 = getelementptr i8, ptr %87, i64 8
%90 = load ptr, ptr %89
%91 = icmp eq ptr %90, null
br i1 %91, label %92, label %95
92:
call void @qsort(ptr %84, i64 %88, i64 8, ptr @i)
%93 = call ptr @calloc(i64 %77, i64 16)
%94 = icmp eq ptr %93, null
br i1 %94, label %132, label %98
95:
%96 = add i64 %88, 1
%97 = getelementptr ptr, ptr %84, i64 %88
store ptr %90, ptr %97
br label %86
98:
%99 = phi i64 [ %120, %112 ], [ 0, %92 ]
%100 = icmp eq i64 %99, %77
br i1 %100, label %121, label %101
101:
%102 = getelementptr ptr, ptr %84, i64 %99
%103 = load ptr, ptr %102
%104 = getelementptr i8, ptr %103, i64 24
%105 = load i64, ptr %104
%106 = icmp eq i64 %105, -1
br i1 %106, label %107, label %108
107:
br label %124
108:
%109 = add i64 %105, 1
%110 = call ptr @malloc(i64 %109)
%111 = icmp eq ptr %110, null
br i1 %111, label %107, label %112
112:
%113 = getelementptr i8, ptr %103, i64 16
%114 = load ptr, ptr %113
call void @llvm.memcpy.p0.p0.i64(ptr %110, ptr %114, i64 %105, i1 false)
%115 = getelementptr i8, ptr %110, i64 %105
store i8 0, ptr %115
%116 = getelementptr %W, ptr %93, i64 %99
store ptr %110, ptr %116
%117 = getelementptr i8, ptr %103, i64 32
%118 = load i64, ptr %117
%119 = getelementptr i8, ptr %116, i64 8
store i64 %118, ptr %119
%120 = add i64 %99, 1
br label %98
121:
br i1 %10, label %123, label %122
122:
store i64 %77, ptr %4
br label %123
123:
call void @free(ptr %84)
call void @g(ptr %8)
call void @free(ptr %22)
call void @h(ptr %29, i64 %30)
br label %137
124:
%125 = phi i64 [ %131, %128 ], [ 0, %107 ]
%126 = icmp eq i64 %125, %77
br i1 %126, label %127, label %128
127:
call void @free(ptr %93)
br label %132
128:
%129 = getelementptr %W, ptr %93, i64 %125
%130 = load ptr, ptr %129
call void @free(ptr %130)
%131 = add i64 %125, 1
br label %124
132:
%133 = phi ptr [ %22, %127 ], [ %22, %71 ], [ null, %18 ], [ null, %21 ], [ %22, %24 ], [ %22, %82 ], [ %22, %92 ], [ %22, %80 ], [ %22, %55 ]
%134 = phi ptr [ %84, %127 ], [ null, %71 ], [ null, %18 ], [ null, %21 ], [ null, %24 ], [ null, %82 ], [ %84, %92 ], [ null, %80 ], [ null, %55 ]
call void @free(ptr %134)
call void @g(ptr %8)
call void @free(ptr %133)
%135 = load ptr, ptr %6
%136 = load i64, ptr %7
call void @h(ptr %135, i64 %136)
br label %137
137:
%138 = phi ptr [ null, %132 ], [ %93, %123 ], [ null, %79 ]
br label %139
139:
%140 = phi ptr [ %138, %137 ], [ null, %14 ], [ null, %12 ]
ret ptr %140
}
declare void @llvm.memset.p0.i64(ptr, i8, i64, i1 immarg)
define internal i32 @a(ptr %0, i64 %1, ptr %2, ptr %3) {
store ptr null, ptr %2
store i64 0, ptr %3
%5 = icmp eq i64 %1, 0
br i1 %5, label %58, label %6
6:
%7 = icmp ugt i64 %1, 768614336404564650
br i1 %7, label %58, label %8
8:
%9 = call ptr @calloc(i64 %1, i64 24)
%10 = icmp eq ptr %9, null
br i1 %10, label %58, label %11
11:
%12 = phi i64 [ %56, %54 ], [ 0, %8 ]
%13 = phi i64 [ %55, %54 ], [ 0, %8 ]
%14 = icmp eq i64 %12, %1
br i1 %14, label %57, label %15
15:
%16 = getelementptr ptr, ptr %0, i64 %12
%17 = load ptr, ptr %16
%18 = icmp eq ptr %17, null
br i1 %18, label %54, label %19
19:
%20 = call i64 @strlen(ptr %17)
%21 = icmp eq i64 %20, -1
br i1 %21, label %22, label %23
22:
call void @h(ptr %9, i64 %13)
br label %58
23:
%24 = add i64 %20, 1
%25 = call ptr @malloc(i64 %24)
%26 = icmp eq ptr %25, null
br i1 %26, label %27, label %28
27:
call void @h(ptr %9, i64 %13)
br label %58
28:
%29 = phi i64 [ %44, %43 ], [ 0, %23 ]
%30 = phi i64 [ %45, %43 ], [ 0, %23 ]
%31 = icmp eq i64 %30, %20
br i1 %31, label %32, label %34
32:
%33 = icmp eq i64 %29, 0
br i1 %33, label %46, label %47
34:
%35 = getelementptr i8, ptr %17, i64 %30
%36 = load i8, ptr %35
%37 = call zeroext i1 @_Z12is_word_charc(i8 signext %36)
br i1 %37, label %38, label %43
38:
%39 = load i8, ptr %35
%40 = call signext i8 @_Z14normalize_charc(i8 signext %39)
%41 = add i64 %29, 1
%42 = getelementptr i8, ptr %25, i64 %29
store i8 %40, ptr %42
br label %43
43:
%44 = phi i64 [ %41, %38 ], [ %29, %34 ]
%45 = add i64 %30, 1
br label %28
46:
call void @free(ptr %25)
br label %54
47:
%48 = getelementptr i8, ptr %25, i64 %29
store i8 0, ptr %48
%49 = getelementptr %I, ptr %9, i64 %13
store ptr %25, ptr %49
%50 = getelementptr i8, ptr %49, i64 8
store i64 %29, ptr %50
%51 = call i64 @d(ptr %25, i64 %29)
%52 = getelementptr i8, ptr %49, i64 16
store i64 %51, ptr %52
%53 = add i64 %13, 1
br label %54
54:
%55 = phi i64 [ %13, %46 ], [ %53, %47 ], [ %13, %15 ]
%56 = add i64 %12, 1
br label %11
57:
store ptr %9, ptr %2
store i64 %13, ptr %3
br label %58
58:
%59 = phi i32 [ 1, %4 ], [ 0, %6 ], [ 0, %8 ], [ 1, %57 ], [ 0, %27 ], [ 0, %22 ]
ret i32 %59
}
define internal ptr @b(ptr %0, ptr %1) {
store i64 0, ptr %1
%3 = call ptr @fopen(ptr %0, ptr @.str)
%4 = icmp eq ptr %3, null
br i1 %4, label %37, label %5
5:
%6 = call i32 @fseek(ptr %3, i64 0, i32 2)
%7 = icmp eq i32 %6, 0
br i1 %7, label %8, label %11
8:
%9 = call i64 @ftell(ptr %3)
%10 = icmp slt i64 %9, 0
br i1 %10, label %11, label %13
11:
%12 = call i32 @fclose(ptr %3)
br label %37
13:
%14 = call i64 @ftell(ptr %3)
%15 = icmp slt i64 %14, 0
br i1 %15, label %19, label %16
16:
%17 = call i32 @fseek(ptr %3, i64 0, i32 0)
%18 = icmp eq i32 %17, 0
br i1 %18, label %21, label %19
19:
%20 = call i32 @fclose(ptr %3)
br label %37
21:
%22 = add i64 %14, 1
%23 = call ptr @malloc(i64 %22)
%24 = icmp eq ptr %23, null
br i1 %24, label %25, label %27
25:
%26 = call i32 @fclose(ptr %3)
br label %37
27:
%28 = icmp eq i64 %14, 0
br i1 %28, label %34, label %29
29:
%30 = call i64 @fread(ptr %23, i64 1, i64 %14, ptr %3)
%31 = icmp eq i64 %30, %14
br i1 %31, label %34, label %32
32:
call void @free(ptr %23)
%33 = call i32 @fclose(ptr %3)
br label %37
34:
%35 = call i32 @fclose(ptr %3)
%36 = getelementptr i8, ptr %23, i64 %14
store i8 0, ptr %36
store i64 %14, ptr %1
br label %37
37:
%38 = phi ptr [ null, %11 ], [ null, %2 ], [ null, %19 ], [ null, %32 ], [ %23, %34 ], [ null, %25 ]
ret ptr %38
}
define internal i32 @c(ptr %0) {
%2 = getelementptr i8, ptr %0, i64 8
%3 = call ptr @calloc(i64 4096, i64 8)
call void @llvm.memset.p0.i64(ptr %2, i8 0, i64 16, i1 false)
store ptr %3, ptr %0
%4 = icmp ne ptr %3, null
%5 = zext i1 %4 to i32
ret i32 %5
}
declare zeroext i1 @_Z12is_word_charc(i8 signext)
declare signext i8 @_Z14normalize_charc(i8 signext)
define internal i64 @d(ptr %0, i64 %1) {
br label %3
3:
%4 = phi i64 [ 1469598103934665603, %2 ], [ %13, %8 ]
%5 = phi i64 [ 0, %2 ], [ %14, %8 ]
%6 = icmp eq i64 %5, %1
br i1 %6, label %7, label %8
7:
ret i64 %4
8:
%9 = getelementptr i8, ptr %0, i64 %5
%10 = load i8, ptr %9
%11 = zext i8 %10 to i64
%12 = xor i64 %4, %11
%13 = mul i64 %12, 1099511628211
%14 = add i64 %5, 1
br label %3
}
define internal i32 @e(ptr %0, i64 %1, ptr %2, i64 %3, i64 %4) {
br label %6
6:
%7 = phi i64 [ 0, %5 ], [ %23, %22 ]
%8 = icmp eq i64 %7, %1
br i1 %8, label %24, label %9
9:
%10 = getelementptr %I, ptr %0, i64 %7
%11 = getelementptr i8, ptr %10, i64 16
%12 = load i64, ptr %11
%13 = icmp eq i64 %12, %4
br i1 %13, label %14, label %22
14:
%15 = getelementptr i8, ptr %10, i64 8
%16 = load i64, ptr %15
%17 = icmp eq i64 %16, %3
br i1 %17, label %18, label %22
18:
%19 = load ptr, ptr %10
%20 = call i32 @bcmp(ptr %19, ptr %2, i64 %3)
%21 = icmp eq i32 %20, 0
br i1 %21, label %24, label %22
22:
%23 = add i64 %7, 1
br label %6
24:
%25 = icmp ult i64 %7, %1
%26 = zext i1 %25 to i32
ret i32 %26
}
define internal i32 @f(ptr %0, ptr %1, i64 %2, i64 %3) {
%5 = and i64 %3, 4095
%6 = load ptr, ptr %0
%7 = getelementptr ptr, ptr %6, i64 %5
br label %8
8:
%9 = phi ptr [ %7, %4 ], [ %10, %16 ]
%10 = load ptr, ptr %9
%11 = icmp eq ptr %10, null
br i1 %11, label %30, label %12
12:
%13 = getelementptr i8, ptr %10, i64 40
%14 = load i64, ptr %13
%15 = icmp eq i64 %14, %3
br i1 %15, label %17, label %16
16:
br label %8
17:
%18 = getelementptr i8, ptr %10, i64 24
%19 = load i64, ptr %18
%20 = icmp eq i64 %19, %2
br i1 %20, label %21, label %16
21:
%22 = getelementptr i8, ptr %10, i64 16
%23 = load ptr, ptr %22
%24 = call i32 @bcmp(ptr %23, ptr %1, i64 %2)
%25 = icmp eq i32 %24, 0
br i1 %25, label %26, label %16
26:
%27 = getelementptr i8, ptr %10, i64 32
%28 = load i64, ptr %27
%29 = add i64 %28, 1
store i64 %29, ptr %27
br label %53
30:
%31 = icmp eq i64 %2, -1
br i1 %31, label %53, label %32
32:
%33 = add i64 %2, 1
%34 = call ptr @malloc(i64 %33)
%35 = call ptr @malloc(i64 48)
%36 = icmp ne ptr %34, null
%37 = icmp ne ptr %35, null
%38 = and i1 %36, %37
br i1 %38, label %40, label %39
39:
call void @free(ptr %34)
call void @free(ptr %35)
br label %53
40:
call void @llvm.memcpy.p0.p0.i64(ptr %34, ptr %1, i64 %2, i1 false)
%41 = getelementptr i8, ptr %34, i64 %2
store i8 0, ptr %41
%42 = getelementptr i8, ptr %35, i64 16
store ptr %34, ptr %42
%43 = getelementptr i8, ptr %35, i64 24
store i64 %2, ptr %43
%44 = getelementptr i8, ptr %35, i64 32
store i64 1, ptr %44
%45 = getelementptr i8, ptr %35, i64 40
store i64 %3, ptr %45
%46 = load ptr, ptr %7
store ptr %46, ptr %35
store ptr %35, ptr %7
%47 = getelementptr i8, ptr %0, i64 8
%48 = load ptr, ptr %47
%49 = getelementptr i8, ptr %35, i64 8
store ptr %48, ptr %49
store ptr %35, ptr %47
%50 = getelementptr i8, ptr %0, i64 16
%51 = load i64, ptr %50
%52 = add i64 %51, 1
store i64 %52, ptr %50
br label %53
53:
%54 = phi i32 [ 1, %26 ], [ 0, %30 ], [ 1, %40 ], [ 0, %39 ]
ret i32 %54
}
define internal void @g(ptr %0) {
%2 = getelementptr i8, ptr %0, i64 8
%3 = load ptr, ptr %2
br label %4
4:
%5 = phi ptr [ %3, %1 ], [ %9, %7 ]
%6 = icmp eq ptr %5, null
br i1 %6, label %12, label %7
7:
%8 = getelementptr i8, ptr %5, i64 8
%9 = load ptr, ptr %8
%10 = getelementptr i8, ptr %5, i64 16
%11 = load ptr, ptr %10
call void @free(ptr %11)
call void @free(ptr %5)
br label %4
12:
%13 = load ptr, ptr %0
call void @free(ptr %13)
ret void
}
declare void @free(ptr allocptr)
define internal void @h(ptr %0, i64 %1) {
%3 = icmp eq ptr %0, null
br i1 %3, label %12, label %4
4:
%5 = phi i64 [ %11, %8 ], [ 0, %2 ]
%6 = icmp eq i64 %5, %1
br i1 %6, label %7, label %8
7:
call void @free(ptr %0)
br label %12
8:
%9 = getelementptr %I, ptr %0, i64 %5
%10 = load ptr, ptr %9
call void @free(ptr %10)
%11 = add i64 %5, 1
br label %4
12:
ret void
}
declare ptr @malloc(i64)
declare void @qsort(ptr, i64, i64, ptr)
define internal i32 @i(ptr %0, ptr %1) {
%3 = load ptr, ptr %0
%4 = load ptr, ptr %1
%5 = getelementptr i8, ptr %3, i64 32
%6 = load i64, ptr %5
%7 = getelementptr i8, ptr %4, i64 32
%8 = load i64, ptr %7
%9 = icmp eq i64 %6, %8
br i1 %9, label %13, label %10
10:
%11 = icmp ugt i64 %6, %8
%12 = select i1 %11, i32 -1, i32 1
br label %19
13:
%14 = getelementptr i8, ptr %3, i64 16
%15 = load ptr, ptr %14
%16 = getelementptr i8, ptr %4, i64 16
%17 = load ptr, ptr %16
%18 = call i32 @strcmp(ptr %15, ptr %17)
br label %19
19:
%20 = phi i32 [ %12, %10 ], [ %18, %13 ]
ret i32 %20
}
declare ptr @calloc(i64, i64)
declare void @llvm.memcpy.p0.p0.i64(ptr, ptr, i64, i1 immarg)
declare i64 @strlen(ptr)
declare ptr @fopen(ptr, ptr)
declare i32 @fseek(ptr, i64, i32)
declare i64 @ftell(ptr)
declare i32 @fclose(ptr)
declare i64 @fread(ptr, i64, i64, ptr)
declare i32 @strcmp(ptr, ptr)
declare i64 @llvm.umin.i64(i64, i64)
declare i32 @bcmp(ptr, ptr, i64)
