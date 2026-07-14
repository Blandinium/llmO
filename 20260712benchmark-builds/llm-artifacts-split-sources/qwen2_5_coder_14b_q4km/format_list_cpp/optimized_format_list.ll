; ModuleID = '/home/tijl/code/llmO/SUT/format_list.cpp'
source_filename = "/home/tijl/code/llmO/SUT/format_list.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"class.std::__cxx11::basic_string" = type { %"struct.std::__cxx11::basic_string<char>::_Alloc_hider", i64, %union.anon }
%"struct.std::__cxx11::basic_string<char>::_Alloc_hider" = type { ptr }
%union.anon = type { i64, [8 x i8] }

$__clang_call_terminate = comdat any

$_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm = comdat any

$_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm = comdat any

@.str.1 = private unnamed_addr constant [3 x i8] c", \00", align 1
@.str.2 = private unnamed_addr constant [2 x i8] c"]\00", align 1
@.str.4 = private unnamed_addr constant [24 x i8] c"basic_string::_M_create\00", align 1
@.str.5 = private unnamed_addr constant [21 x i8] c"basic_string::append\00", align 1
@__const._ZNSt8__detail18__to_chars_10_implIjEEvPcjT_.__digits = private unnamed_addr constant [201 x i8] c"00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899\00", align 16

; Function Attrs: mustprogress uwtable
define noundef ptr @format_list(ptr noundef readonly %input, i64 noundef %input_length) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %result = alloca %"class.std::__cxx11::basic_string", align 8
  %ref.tmp8 = alloca %"class.std::__cxx11::basic_string", align 8
  %cmp = icmp eq ptr %input, null
  %cmp1 = icmp ne i64 %input_length, 0
  %or.cond = and i1 %cmp, %cmp1
  br i1 %or.cond, label %return, label %if.end

if.end:                                           ; preds = %entry
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %result) #13
  %0 = getelementptr inbounds nuw i8, ptr %result, i64 16
  store ptr %0, ptr %result, align 8, !tbaa !4
  store i8 91, ptr %0, align 8, !tbaa !10
  %_M_string_length.i.i.i.i = getelementptr inbounds nuw i8, ptr %result, i64 8
  store i64 1, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %arrayidx.i.i.i = getelementptr inbounds nuw i8, ptr %result, i64 17
  store i8 0, ptr %arrayidx.i.i.i, align 1, !tbaa !10
  %cmp2109.not = icmp eq i64 %input_length, 0
  br i1 %cmp2109.not, label %for.cond.cleanup, label %for.body.lr.ph

for.body.lr.ph:                                   ; preds = %if.end
  %1 = getelementptr inbounds nuw i8, ptr %ref.tmp8, i64 16
  %_M_string_length.i.i.i.i62 = getelementptr inbounds nuw i8, ptr %ref.tmp8, i64 8
  br label %for.body

for.body:                                         ; preds = %for.body.lr.ph, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit
  %i.0110 = phi i64 [ 0, %for.body.lr.ph ], [ %inc, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit ]
  %cmp3.not = icmp eq i64 %i.0110, 0
  br i1 %cmp3.not, label %if.end7, label %if.then4

if.then4:                                         ; preds = %for.body
  %6 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %7 = and i64 %6, -2
  %cmp.i.i.i38 = icmp eq i64 %7, 9223372036854775806
  br i1 %cmp.i.i.i38, label %if.then.i.i.i56, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i39

if.then.i.i.i56:                                  ; preds = %if.then4
  invoke void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.5) #14
          to label %.noexc57 unwind label %lpad5.loopexit.split-lp

.noexc57:                                         ; preds = %if.then.i.i.i56
  unreachable

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i39: ; preds = %if.then4
  %add.i.i.i40 = add i64 %6, 2
  %8 = load ptr, ptr %result, align 8, !tbaa !14
  %cmp.i.i.i.i.i41 = icmp eq ptr %8, %0
  br i1 %cmp.i.i.i.i.i41, label %if.then.i.i.i.i.i54, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i42

if.then.i.i.i.i.i54:                              ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i39
  %cmp3.i.i.i.i.i55 = icmp ult i64 %6, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i55)
  br label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i42

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i42: ; preds = %if.then.i.i.i.i.i54, %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i39
  %9 = load i64, ptr %0, align 8
  %cond.i.i.i.i43 = select i1 %cmp.i.i.i.i.i41, i64 15, i64 %9
  %cmp.not.i.i.i44 = icmp ugt i64 %add.i.i.i40, %cond.i.i.i.i43
  br i1 %cmp.not.i.i.i44, label %if.else.i.i.i53, label %if.end.i.i.i.i.i50

if.end.i.i.i.i.i50:                               ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i42
  %add.ptr.i.i.i48 = getelementptr inbounds nuw i8, ptr %8, i64 %6
  store i16 8236, ptr %add.ptr.i.i.i48, align 1
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit59

if.else.i.i.i53:                                  ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i42
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %result, i64 noundef %6, i64 noundef 0, ptr noundef nonnull @.str.1, i64 noundef 2)
          to label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit59 unwind label %lpad5.loopexit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit59: ; preds = %if.else.i.i.i53, %if.end.i.i.i.i.i50
  store i64 %add.i.i.i40, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %10 = load ptr, ptr %result, align 8, !tbaa !14
  %arrayidx.i.i.i.i51 = getelementptr inbounds nuw i8, ptr %10, i64 %add.i.i.i40
  store i8 0, ptr %arrayidx.i.i.i.i51, align 1, !tbaa !10
  br label %if.end7

if.end7:                                          ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit59, %for.body
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %ref.tmp8) #13
  %arrayidx = getelementptr inbounds nuw i32, ptr %input, i64 %i.0110
  %11 = load i32, ptr %arrayidx, align 4, !tbaa !15
  call void @llvm.experimental.noalias.scope.decl(metadata !17)
  %__val.lobit.i = lshr i32 %11, 31
  %storedv.i = zext nneg i32 %__val.lobit.i to i64
  %cond.i = call i32 @llvm.abs.i32(i32 %11, i1 false)
  %cmp39.i.i = icmp ult i32 %cond.i, 10
  br i1 %cmp39.i.i, label %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i, label %if.end.i.i60

if.end.i.i60:                                     ; preds = %if.end7, %if.end14.i.i
  %__value.addr.041.i.i = phi i32 [ %12, %if.end14.i.i ], [ %cond.i, %if.end7 ]
  %__n.040.i.i = phi i32 [ %add17.i.i, %if.end14.i.i ], [ 1, %if.end7 ]
  %cmp3.i.i = icmp ult i32 %__value.addr.041.i.i, 100
  br i1 %cmp3.i.i, label %if.then4.i.i, label %if.end5.i.i

if.then4.i.i:                                     ; preds = %if.end.i.i60
  %add.i.i = add i32 %__n.040.i.i, 1
  br label %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i

if.end5.i.i:                                      ; preds = %if.end.i.i60
  %cmp6.i.i = icmp ult i32 %__value.addr.041.i.i, 1000
  br i1 %cmp6.i.i, label %if.then7.i.i, label %if.end9.i.i

if.then7.i.i:                                     ; preds = %if.end5.i.i
  %add8.i.i = add i32 %__n.040.i.i, 2
  br label %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i

if.end9.i.i:                                      ; preds = %if.end5.i.i
  %cmp11.i.i = icmp ult i32 %__value.addr.041.i.i, 10000
  br i1 %cmp11.i.i, label %if.then12.i.i, label %if.end14.i.i

if.then12.i.i:                                    ; preds = %if.end9.i.i
  %add13.i.i = add i32 %__n.040.i.i, 3
  br label %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i

if.end14.i.i:                                     ; preds = %if.end9.i.i
  %12 = udiv i32 %__value.addr.041.i.i, 10000
  %add17.i.i = add i32 %__n.040.i.i, 4
  %cmp.i.i61 = icmp ult i32 %__value.addr.041.i.i, 100000
  br i1 %cmp.i.i61, label %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i, label %if.end.i.i60, !llvm.loop !20

_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i:    ; preds = %if.end14.i.i, %if.then12.i.i, %if.then7.i.i, %if.then4.i.i, %if.end7
  %retval.0.i.i = phi i32 [ %add.i.i, %if.then4.i.i ], [ %add8.i.i, %if.then7.i.i ], [ %add13.i.i, %if.then12.i.i ], [ 1, %if.end7 ], [ %add17.i.i, %if.end14.i.i ]
  store ptr %1, ptr %ref.tmp8, align 8, !tbaa !4, !alias.scope !17
  store i64 0, ptr %_M_string_length.i.i.i.i62, align 8, !tbaa !11, !alias.scope !17
  store i8 0, ptr %1, align 8, !tbaa !10, !alias.scope !17
  %add2.i = add i32 %retval.0.i.i, %__val.lobit.i
  %conv3.i = zext i32 %add2.i to i64
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm(ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp8, i64 noundef %conv3.i)
          to label %.noexc.i unwind label %terminate.lpad.i

.noexc.i:                                         ; preds = %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i
  %13 = load ptr, ptr %ref.tmp8, align 8, !tbaa !14, !alias.scope !17
  store i8 45, ptr %13, align 1, !tbaa !10
  %add.ptr.i.i.i.i = getelementptr inbounds nuw i8, ptr %13, i64 %storedv.i
  %cmp34.i.i.i.i.i = icmp ugt i32 %cond.i, 99
  br i1
