```llvm
; ModuleID = 'format_list.cpp'
source_filename = "format_list.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

@.str = private unnamed_addr constant [3 x i8] c", \00", align 1
@.str.1 = private unnamed_addr constant [2 x i8] c"]\00", align 1
@.str.2 = private unnamed_addr constant [2 x i8] c"[\00", align 1

; Function Attrs: mustprogress uwtable
define noundef ptr @format_list(ptr noundef readonly %input, i64 noundef %input_length) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %cmp = icmp eq i64 %input_length, 0
  br i1 %cmp, label %return_empty, label %check_length

return_empty:
  %result_empty = call noundef ptr @_Znwm(i64 noundef 3) #7
  %result_empty_ptr = getelementptr inbounds i8, ptr %result_empty, i64 0
  store i8 91, ptr %result_empty_ptr, align 1
  %result_empty_ptr1 = getelementptr inbounds i8, ptr %result_empty, i64 1
  store i8 93, ptr %result_empty_ptr1, align 1
  %result_empty_ptr2 = getelementptr inbounds i8, ptr %result_empty, i64 2
  store i8 0, ptr %result_empty_ptr2, align 1
  ret ptr %result_empty

check_length:
  %cmp1 = icmp eq ptr %input, null
  br i1 %cmp1, label %return_null, label %format_list_loop

return_null:
  ret ptr null

format_list_loop:
  %result = call noundef ptr @_Znwm(i64 noundef 32) #7
  %result_ptr = getelementptr inbounds i8, ptr %result, i64 0
  store i8 91, ptr %result_ptr, align 1
  %result_ptr1 = getelementptr inbounds i8, ptr %result, i64 1
  store i8 0, ptr %result_ptr1, align 1
  %result_ptr2 = getelementptr inbounds i8, ptr %result, i64 2
  store i8 0, ptr %result_ptr2, align 1
  %result_ptr3 = getelementptr inbounds i8, ptr %result, i64 3
  store i8 0, ptr %result_ptr3, align 1
  %result_ptr4 = getelementptr inbounds i8, ptr %result, i64 4
  store i8 0, ptr %result_ptr4, align 1
  %result_ptr5 = getelementptr inbounds i8, ptr %result, i64 5
  store i8 0, ptr %result_ptr5, align 1
  %result_ptr6 = getelementptr inbounds i8, ptr %result, i64 6
  store i8 0, ptr %result_ptr6, align 1
  %result_ptr7 = getelementptr inbounds i8, ptr %result, i64 7
  store i8 0, ptr %result_ptr7, align 1
  %result_ptr8 = getelementptr inbounds i8, ptr %result, i64 8
  store i8 0, ptr %result_ptr8, align 1
  %result_ptr9 = getelementptr inbounds i8, ptr %result, i64 9
  store i8 0, ptr %result_ptr9, align 1
  %result_ptr10 = getelementptr inbounds i8, ptr %result, i64 10
  store i8 0, ptr %result_ptr10, align 1
  %result_ptr11 = getelementptr inbounds i8, ptr %result, i64 11
  store i8 0, ptr %result_ptr11, align 1
  %result_ptr12 = getelementptr inbounds i8, ptr %result, i64 12
  store i8 0, ptr %result_ptr12, align 1
  %result_ptr13 = getelementptr inbounds i8, ptr %result, i64 13
  store i8 0, ptr %result_ptr13, align 1
  %result_ptr14 = getelementptr inbounds i8, ptr %result, i64 14
  store i8 0, ptr %result_ptr14, align 1
  %result_ptr15 = getelementptr inbounds i8, ptr %result, i64 15
  store i8 0, ptr %result_ptr15, align 1
  %result_ptr16 = getelementptr inbounds i8, ptr %result, i64 16
  store i8 0, ptr %result_ptr16, align 1
  %result_ptr17 = getelementptr inbounds i8, ptr %result, i64 17
  store i8 0, ptr %result_ptr17, align 1
  %result_ptr18 = getelementptr inbounds i8, ptr %result, i64 18
  store i8 0, ptr %result_ptr18, align 1
  %result_ptr19 = getelementptr inbounds i8, ptr %result, i64 19
  store i8 0, ptr %result_ptr19, align 1
  %result_ptr20 = getelementptr inbounds i8, ptr %result, i64 20
  store i8 0, ptr %result_ptr20, align 1
  %result_ptr21 = getelementptr inbounds i8, ptr %result, i64 21
  store i8 0, ptr %result_ptr21, align 1
  %result_ptr22 = getelementptr inbounds i8, ptr %result, i64 22
  store i8 0, ptr %result_ptr22, align 1
  %result_ptr23 = getelementptr inbounds i8, ptr %result, i64 23
  store i8 0, ptr %result_ptr23, align 1
  %result_ptr24 = getelementptr inbounds i8, ptr %result, i64 24
  store i8 0, ptr %result_ptr24, align 1
  %result_ptr25 = getelementptr inbounds i8, ptr %result, i64 25
  store i8 0, ptr %result_ptr25, align 1
  %result_ptr26 = getelementptr inbounds i8, ptr %result, i64 26
  store i8 0, ptr %result_ptr26, align 1
  %result_ptr27 = getelementptr inbounds i8, ptr %result, i64 27
  store i8 0, ptr %result_ptr27, align 1
  %result_ptr28 = getelementptr inbounds i8, ptr %result, i64 28
  store i8 0, ptr %result_ptr28, align 1
  %result_ptr29 = getelementptr inbounds i8, ptr %result, i64 29
  store i8 0, ptr %result_ptr29, align 1
  %result_ptr30 = getelementptr inbounds i8, ptr %result, i64 30
  store i8 0, ptr %result_ptr30, align 1
  %result_ptr31 = getelementptr inbounds i8, ptr %result, i64 31
  store i8 0, ptr %result_ptr31, align 1
  %result_ptr32 = getelementptr inbounds i8, ptr %result, i64 32
  store i8 0, ptr %result_ptr32, align 1
  %result_ptr33 = getelementptr inbounds i8, ptr %result, i64 33
  store i8 0, ptr %result_ptr33, align 1
  %result_ptr34 = getelementptr inbounds i8, ptr %result, i64 34
  store i8 0, ptr %result_ptr34, align 1
  %result_ptr35 = getelementptr inbounds i8, ptr %result, i64 35
  store i8 0, ptr %result_ptr35, align 1
  %result_ptr36 = getelementptr inbounds i8, ptr %result, i64 36
  store i8 0, ptr %result_ptr36, align 1
  %result_ptr37 = getelementptr inbounds i8, ptr %result, i64 37
  store i8 0, ptr %result_ptr37, align 1
  %result_ptr38 = getelementptr inbounds i8, ptr %result, i64 38
  store i8 0, ptr %result_ptr38, align 1
  %result_ptr39 = getelementptr inbounds i8, ptr %result, i64 39
  store i8 0, ptr %result_ptr39, align 1
  %result_ptr40 = getelementptr inbounds i8, ptr %result, i64 40
  store i8 0, ptr %result_ptr40, align 1
  %result_ptr41 = getelementptr inbounds i8, ptr %result, i64 41
  store i8 0, ptr %result_ptr41, align 1
  %result_ptr42 = getelementptr inbounds i8, ptr %result, i64 42
  store i8 0, ptr %result_ptr42, align 1
  %result_ptr43 = getelementptr inbounds i8, ptr %result, i64 43
  store i8 0, ptr %result_ptr43, align 1
  %result_ptr44 = getelementptr inbounds i8, ptr %result, i64 44
  store i8 0, ptr %result_ptr44, align 1
  %result_ptr45 = getelementptr inbounds i8, ptr %result, i64 45
  store i8 0, ptr %result_ptr45, align 1
  %result_ptr46 = getelementptr inbounds i8, ptr %result, i64 46
  store i8 0, ptr %result_ptr46, align 1
  %result_ptr47 = getelementptr inbounds i8, ptr %result, i64 47
  store i8 0, ptr %result_ptr47, align 1
  %result_ptr48 = getelementptr inbounds i8, ptr %result, i64 48
  store i8 0, ptr %result_ptr48, align 1
  %result_ptr49 = getelementptr inbounds i8, ptr %result, i64 49
  store i8 0, ptr %result_ptr49, align 1
  %result_ptr50 = getelementptr inbounds i8, ptr %result, i64 50
  store i8 0, ptr %result_ptr50, align 1
  %result_ptr51 = getelementptr inbounds i8, ptr %result, i64 51
  store i8 0, ptr %result_ptr51, align 1
  %result_ptr52 = getelementptr inbounds i8, ptr %result, i64 52
  store i8 0, ptr %result_ptr52, align 1
  %result_ptr53 = getelementptr inbounds i8, ptr %result, i64 53
  store i8 0, ptr %result_ptr53, align 1
  %result_ptr54 = getelementptr inbounds i8, ptr %result, i64 54
  store i8 0, ptr %result_ptr54, align 1
  %result_ptr55 = getelementptr inbounds i8, ptr %result, i64 55
  store i8 0, ptr %result_ptr55, align 1
  %result_ptr56 = getelementptr inbounds i8, ptr %result, i64 56
  store i8 0, ptr %result_ptr56, align 1
  %result_ptr57 = getelementptr inbounds i8, ptr %result, i64 57
  store i8 0, ptr %result_ptr57, align 1
  %result_ptr58 = getelementptr inbounds i8, ptr %result, i64 58
  store i8 0, ptr %result_ptr58, align 1
  %result_ptr59 = getelementptr inbounds i8, ptr %result, i64 59
  store i8 0, ptr %result_ptr59, align 1
  %result_ptr60 = getelementptr inbounds i8, ptr %result, i64 60
  store i8 0, ptr %result_ptr60, align 1
  %result_ptr61 = getelementptr inbounds i8, ptr %result, i64 61
  store i8 0, ptr %result_ptr61, align 1
  %result_ptr62 = getelementptr inbounds i8, ptr %result, i64 62
  store i8 0, ptr %result_ptr62, align 1
  %result_ptr63 = getelementptr inbounds i8, ptr %result, i64 63
  store i8 0, ptr %result_ptr63, align 1
  %result_ptr64 = getelementptr inbounds i8, ptr %result, i64 64
  store i8 0, ptr %result_ptr64, align 1
  %result_ptr65 = getelementptr inbounds i8, ptr %result, i64 65
  store i8 0, ptr %result_ptr65, align 1
  %result_ptr66 = getelementptr inbounds i8, ptr %result, i64 66
  store i8 0, ptr %result_ptr66, align 1
  %result_ptr67 = getelementptr inbounds i8, ptr %result, i64 67
  store i8 0, ptr %result_ptr67, align 1
  %result_ptr68 = getelementptr inbounds i8, ptr %result, i64 68
  store i8 0, ptr %result_ptr68, align 1
  %result_ptr69 = getelementptr inbounds i8, ptr %result, i64 69
  store i8 0, ptr %result_ptr69, align 1
  %result_ptr70 = getelementptr inbounds i8, ptr %result, i64 70
  store i8 0, ptr %result_ptr70, align 1
  %result_ptr71 = getelementptr inbounds i8, ptr %result, i64 71
  store i8 0, ptr %result_ptr71, align 1
  %result_ptr72 = getelementptr inbounds i8, ptr %result, i64 72
  store i8 0, ptr %result_ptr72, align 1
  %result_ptr73 = getelementptr inbounds i8, ptr %result, i64 73
  store i8 0, ptr %result_ptr73, align 1
  %result_ptr74 = getelementptr inbounds i8, ptr %result, i64 74
  store i8 0, ptr %result_ptr74, align 1
  %result_ptr75 = getelementptr inbounds i8, ptr %result, i64 75
  store i8 0, ptr %result_ptr75, align 1
  %result_ptr76 = getelementptr inbounds i8, ptr %result, i64 76
  store i8 0, ptr %result_ptr76, align 1
  %result_ptr77 = getelementptr inbounds i8, ptr %result, i64 77
  store i8 0, ptr %result_ptr77, align 1
  %result_ptr78 = getelementptr inbounds i8, ptr %result, i64 78
  store i8 0, ptr %result_ptr78, align 1
  %result_ptr79 = getelementptr inbounds i8, ptr %result, i64 79
  store i8 0, ptr %result_ptr79, align 1
  %result_ptr80 = getelementptr inbounds i8, ptr %result, i64 80
  store i8 0, ptr %result_ptr80, align 1
  %result_ptr81 = getelementptr inbounds i8, ptr %result, i64 81
  store i8 0, ptr %result_ptr81, align 1
  %result
