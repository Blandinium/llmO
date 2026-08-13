; ModuleID = '/home/tijl/code/llmO/results/extracted-ir/20260807_full_run-extracted-ir/qwen2-5-coder-14b-q4km/format_list_cpp/input_extraction/assemble/input.bc'
source_filename = "/home/tijl/code/llmO/SUT/format_list.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"class.std::__cxx11::basic_string" = type { %"struct.std::__cxx11::basic_string<char>::_Alloc_hider", i64, %union.anon }
%"struct.std::__cxx11::basic_string<char>::_Alloc_hider" = type { ptr }
%union.anon = type { i64, [8 x i8] }

@.str.1 = external hidden unnamed_addr constant [3 x i8], align 1
@.str.2 = external hidden unnamed_addr constant [2 x i8], align 1
@.str.5 = external hidden unnamed_addr constant [21 x i8], align 1
@__const._ZNSt8__detail18__to_chars_10_implIjEEvPcjT_.__digits = external hidden unnamed_addr constant [201 x i8], align 16

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
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %result) #10
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

for.cond.cleanup:                                 ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit, %if.end
  %2 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %cmp.i.i.i27 = icmp eq i64 %2, 9223372036854775807
  br i1 %cmp.i.i.i27, label %if.then.i.i.i32, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i

if.then.i.i.i32:                                  ; preds = %for.cond.cleanup
  invoke void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.5) #11
          to label %.noexc33 unwind label %lpad12

.noexc33:                                         ; preds = %if.then.i.i.i32
  unreachable

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i: ; preds = %for.cond.cleanup
  %add.i.i.i28 = add i64 %2, 1
  %3 = load ptr, ptr %result, align 8, !tbaa !14
  %cmp.i.i.i.i.i29 = icmp eq ptr %3, %0
  br i1 %cmp.i.i.i.i.i29, label %if.then.i.i.i.i.i, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i

if.then.i.i.i.i.i:                                ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i
  %cmp3.i.i.i.i.i = icmp ult i64 %2, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i)
  br label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i: ; preds = %if.then.i.i.i.i.i, %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i
  %4 = load i64, ptr %0, align 8
  %cond.i.i.i.i = select i1 %cmp.i.i.i.i.i29, i64 15, i64 %4
  %cmp.not.i.i.i = icmp ugt i64 %add.i.i.i28, %cond.i.i.i.i
  br i1 %cmp.not.i.i.i, label %if.else.i.i.i, label %if.then.i.i.i.i31

if.then.i.i.i.i31:                                ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i
  %add.ptr.i.i.i = getelementptr inbounds nuw i8, ptr %3, i64 %2
  store i8 93, ptr %add.ptr.i.i.i, align 1, !tbaa !10
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit

if.else.i.i.i:                                    ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %result, i64 noundef %2, i64 noundef 0, ptr noundef nonnull @.str.2, i64 noundef 1)
          to label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit unwind label %lpad12

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit: ; preds = %if.else.i.i.i, %if.then.i.i.i.i31
  store i64 %add.i.i.i28, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %5 = load ptr, ptr %result, align 8, !tbaa !14
  %arrayidx.i.i.i.i = getelementptr inbounds nuw i8, ptr %5, i64 %add.i.i.i28
  store i8 0, ptr %arrayidx.i.i.i.i, align 1, !tbaa !10
  %call16 = invoke noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32) %result)
          to label %invoke.cont15 unwind label %lpad12

for.body:                                         ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit, %for.body.lr.ph
  %i.0110 = phi i64 [ 0, %for.body.lr.ph ], [ %inc, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit ]
  %cmp3.not = icmp eq i64 %i.0110, 0
  br i1 %cmp3.not, label %if.end7, label %if.then4

if.then4:                                         ; preds = %for.body
  %6 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %7 = and i64 %6, -2
  %cmp.i.i.i38 = icmp eq i64 %7, 9223372036854775806
  br i1 %cmp.i.i.i38, label %if.then.i.i.i56, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i39

if.then.i.i.i56:                                  ; preds = %if.then4
  invoke void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.5) #11
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

lpad5.loopexit:                                   ; preds = %if.else.i.i.i53
  %lpad.loopexit = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup17

lpad5.loopexit.split-lp:                          ; preds = %if.then.i.i.i56
  %lpad.loopexit.split-lp = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup17

if.end7:                                          ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit59, %for.body
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %ref.tmp8) #10
  %arrayidx = getelementptr inbounds nuw i32, ptr %input, i64 %i.0110
  %11 = load i32, ptr %arrayidx, align 4, !tbaa !15
  call void @llvm.experimental.noalias.scope.decl(metadata !17)
  %__val.lobit.i = lshr i32 %11, 31
  %storedv.i = zext nneg i32 %__val.lobit.i to i64
  %cond.i = call i32 @llvm.abs.i32(i32 %11, i1 false)
  %cmp39.i.i = icmp ult i32 %cond.i, 10
  br i1 %cmp39.i.i, label %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i, label %if.end.i.i60

if.end.i.i60:                                     ; preds = %if.end14.i.i, %if.end7
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
  br i1 %cmp34.i.i.i.i.i, label %while.body.preheader.i.i.i.i.i, label %while.end.i.i.i.i.i

while.body.preheader.i.i.i.i.i:                   ; preds = %.noexc.i
  %sub.i.i.i.i.i = add i32 %retval.0.i.i, -1
  br label %while.body.i.i.i.i.i

while.body.i.i.i.i.i:                             ; preds = %while.body.i.i.i.i.i, %while.body.preheader.i.i.i.i.i
  %__val.addr.036.i.i.i.i.i = phi i32 [ %div.i.i.i.i.i, %while.body.i.i.i.i.i ], [ %cond.i, %while.body.preheader.i.i.i.i.i ]
  %__pos.035.i.i.i.i.i = phi i32 [ %sub8.i.i.i.i.i, %while.body.i.i.i.i.i ], [ %sub.i.i.i.i.i, %while.body.preheader.i.i.i.i.i ]
  %rem.i.i.i.i.i = urem i32 %__val.addr.036.i.i.i.i.i, 100
  %mul.i.i.i.i.i = shl nuw nsw i32 %rem.i.i.i.i.i, 1
  %div.i.i.i.i.i = udiv i32 %__val.addr.036.i.i.i.i.i, 100
  %add.i.i.i.i.i = or disjoint i32 %mul.i.i.i.i.i, 1
  %idxprom.i.i.i.i.i = zext nneg i32 %add.i.i.i.i.i to i64
  %arrayidx.i.i.i.i.i = getelementptr inbounds nuw [201 x i8], ptr @__const._ZNSt8__detail18__to_chars_10_implIjEEvPcjT_.__digits, i64 0, i64 %idxprom.i.i.i.i.i
  %14 = load i8, ptr %arrayidx.i.i.i.i.i, align 1, !tbaa !10, !noalias !17
  %idxprom1.i.i.i.i.i = zext i32 %__pos.035.i.i.i.i.i to i64
  %arrayidx2.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %add.ptr.i.i.i.i, i64 %idxprom1.i.i.i.i.i
  store i8 %14, ptr %arrayidx2.i.i.i.i.i, align 1, !tbaa !10
  %idxprom3.i.i.i.i.i = zext nneg i32 %mul.i.i.i.i.i to i64
  %arrayidx4.i.i.i.i.i = getelementptr inbounds nuw [201 x i8], ptr @__const._ZNSt8__detail18__to_chars_10_implIjEEvPcjT_.__digits, i64 0, i64 %idxprom3.i.i.i.i.i
  %15 = load i8, ptr %arrayidx4.i.i.i.i.i, align 2, !tbaa !10, !noalias !17
  %sub5.i.i.i.i.i = add i32 %__pos.035.i.i.i.i.i, -1
  %idxprom6.i.i.i.i.i = zext i32 %sub5.i.i.i.i.i to i64
  %arrayidx7.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %add.ptr.i.i.i.i, i64 %idxprom6.i.i.i.i.i
  store i8 %15, ptr %arrayidx7.i.i.i.i.i, align 1, !tbaa !10
  %sub8.i.i.i.i.i = add i32 %__pos.035.i.i.i.i.i, -2
  %cmp.i.i.i.i.i64 = icmp ugt i32 %__val.addr.036.i.i.i.i.i, 9999
  br i1 %cmp.i.i.i.i.i64, label %while.body.i.i.i.i.i, label %while.end.i.i.i.i.i, !llvm.loop !23

while.end.i.i.i.i.i:                              ; preds = %while.body.i.i.i.i.i, %.noexc.i
  %__val.addr.0.lcssa.i.i.i.i.i = phi i32 [ %cond.i, %.noexc.i ], [ %div.i.i.i.i.i, %while.body.i.i.i.i.i ]
  %cmp9.i.i.i.i.i = icmp samesign ugt i32 %__val.addr.0.lcssa.i.i.i.i.i, 9
  br i1 %cmp9.i.i.i.i.i, label %if.then.i.i.i.i.i63, label %if.else.i.i.i.i.i

if.then.i.i.i.i.i63:                              ; preds = %while.end.i.i.i.i.i
  %mul11.i.i.i.i.i = shl nuw nsw i32 %__val.addr.0.lcssa.i.i.i.i.i, 1
  %add12.i.i.i.i.i = or disjoint i32 %mul11.i.i.i.i.i, 1
  %idxprom13.i.i.i.i.i = zext nneg i32 %add12.i.i.i.i.i to i64
  %arrayidx14.i.i.i.i.i = getelementptr inbounds nuw [201 x i8], ptr @__const._ZNSt8__detail18__to_chars_10_implIjEEvPcjT_.__digits, i64 0, i64 %idxprom13.i.i.i.i.i
  %16 = load i8, ptr %arrayidx14.i.i.i.i.i, align 1, !tbaa !10, !noalias !17
  %arrayidx15.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %add.ptr.i.i.i.i, i64 1
  store i8 %16, ptr %arrayidx15.i.i.i.i.i, align 1, !tbaa !10
  %idxprom16.i.i.i.i.i = zext nneg i32 %mul11.i.i.i.i.i to i64
  %arrayidx17.i.i.i.i.i = getelementptr inbounds nuw [201 x i8], ptr @__const._ZNSt8__detail18__to_chars_10_implIjEEvPcjT_.__digits, i64 0, i64 %idxprom16.i.i.i.i.i
  %17 = load i8, ptr %arrayidx17.i.i.i.i.i, align 2, !tbaa !10, !noalias !17
  br label %_ZNSt7__cxx119to_stringEi.exit

if.else.i.i.i.i.i:                                ; preds = %while.end.i.i.i.i.i
  %18 = trunc nuw i32 %__val.addr.0.lcssa.i.i.i.i.i to i8
  %conv.i.i.i.i.i = or disjoint i8 %18, 48
  br label %_ZNSt7__cxx119to_stringEi.exit

terminate.lpad.i:                                 ; preds = %_ZNSt8__detail14__to_chars_lenIjEEjT_i.exit.i
  %19 = landingpad { ptr, i32 }
          catch ptr null
  %20 = extractvalue { ptr, i32 } %19, 0
  call void @__clang_call_terminate(ptr %20) #12
  unreachable

_ZNSt7__cxx119to_stringEi.exit:                   ; preds = %if.else.i.i.i.i.i, %if.then.i.i.i.i.i63
  %storemerge.i.i.i.i.i = phi i8 [ %conv.i.i.i.i.i, %if.else.i.i.i.i.i ], [ %17, %if.then.i.i.i.i.i63 ]
  store i8 %storemerge.i.i.i.i.i, ptr %add.ptr.i.i.i.i, align 1, !tbaa !10
  store i64 %conv3.i, ptr %_M_string_length.i.i.i.i62, align 8, !tbaa !11, !alias.scope !17
  %21 = load ptr, ptr %ref.tmp8, align 8, !tbaa !14, !alias.scope !17
  %arrayidx.i.i8.i.i.i = getelementptr inbounds nuw i8, ptr %21, i64 %conv3.i
  store i8 0, ptr %arrayidx.i.i8.i.i.i, align 1, !tbaa !10
  %22 = load ptr, ptr %ref.tmp8, align 8, !tbaa !14
  %23 = load i64, ptr %_M_string_length.i.i.i.i62, align 8, !tbaa !11
  %24 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %sub3.i.i.i.i = sub i64 9223372036854775807, %24
  %cmp.i.i.i.i = icmp ult i64 %sub3.i.i.i.i, %23
  br i1 %cmp.i.i.i.i, label %if.then.i.i.i.i69, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i.i

if.then.i.i.i.i69:                                ; preds = %_ZNSt7__cxx119to_stringEi.exit
  invoke void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.5) #11
          to label %.noexc70 unwind label %lpad9.loopexit.split-lp

.noexc70:                                         ; preds = %if.then.i.i.i.i69
  unreachable

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i.i: ; preds = %_ZNSt7__cxx119to_stringEi.exit
  %add.i.i.i.i = add i64 %24, %23
  %25 = load ptr, ptr %result, align 8, !tbaa !14
  %cmp.i.i.i.i.i.i = icmp eq ptr %25, %0
  br i1 %cmp.i.i.i.i.i.i, label %if.then.i.i.i.i.i.i, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i

if.then.i.i.i.i.i.i:                              ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i.i
  %cmp3.i.i.i.i.i.i = icmp ult i64 %24, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i.i)
  br label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i: ; preds = %if.then.i.i.i.i.i.i, %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE15_M_check_lengthEmmPKc.exit.i.i.i
  %26 = load i64, ptr %0, align 8
  %cond.i.i.i.i.i = select i1 %cmp.i.i.i.i.i.i, i64 15, i64 %26
  %cmp.not.i.i.i.i = icmp ugt i64 %add.i.i.i.i, %cond.i.i.i.i.i
  br i1 %cmp.not.i.i.i.i, label %if.else.i.i.i.i, label %if.then.i4.i.i.i

if.then.i4.i.i.i:                                 ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i
  %tobool.not.i.i.i.i = icmp eq i64 %23, 0
  br i1 %tobool.not.i.i.i.i, label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLERKS4_.exit, label %if.then3.i.i.i.i

if.then3.i.i.i.i:                                 ; preds = %if.then.i4.i.i.i
  %add.ptr.i.i.i.i65 = getelementptr inbounds nuw i8, ptr %25, i64 %24
  %cond.i.i.i.i66 = icmp eq i64 %23, 1
  br i1 %cond.i.i.i.i66, label %if.then.i.i.i.i.i68, label %if.end.i.i.i.i.i.i

if.then.i.i.i.i.i68:                              ; preds = %if.then3.i.i.i.i
  %27 = load i8, ptr %22, align 1, !tbaa !10
  store i8 %27, ptr %add.ptr.i.i.i.i65, align 1, !tbaa !10
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLERKS4_.exit

if.end.i.i.i.i.i.i:                               ; preds = %if.then3.i.i.i.i
  call void @llvm.memcpy.p0.p0.i64(ptr align 1 %add.ptr.i.i.i.i65, ptr align 1 %22, i64 %23, i1 false)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLERKS4_.exit

if.else.i.i.i.i:                                  ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %result, i64 noundef %24, i64 noundef 0, ptr noundef %22, i64 noundef %23)
          to label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLERKS4_.exit unwind label %lpad9.loopexit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLERKS4_.exit: ; preds = %if.else.i.i.i.i, %if.end.i.i.i.i.i.i, %if.then.i.i.i.i.i68, %if.then.i4.i.i.i
  store i64 %add.i.i.i.i, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %28 = load ptr, ptr %result, align 8, !tbaa !14
  %arrayidx.i.i.i.i.i67 = getelementptr inbounds nuw i8, ptr %28, i64 %add.i.i.i.i
  store i8 0, ptr %arrayidx.i.i.i.i.i67, align 1, !tbaa !10
  %29 = load ptr, ptr %ref.tmp8, align 8, !tbaa !14
  %cmp.i.i.i72 = icmp eq ptr %29, %1
  br i1 %cmp.i.i.i72, label %if.then.i.i.i75, label %if.then.i.i73

if.then.i.i.i75:                                  ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLERKS4_.exit
  %30 = load i64, ptr %_M_string_length.i.i.i.i62, align 8, !tbaa !11
  %cmp3.i.i.i = icmp ult i64 %30, 16
  call void @llvm.assume(i1 %cmp3.i.i.i)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit

if.then.i.i73:                                    ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLERKS4_.exit
  %31 = load i64, ptr %1, align 8, !tbaa !10
  %add.i.i.i74 = add i64 %31, 1
  call void @_ZdlPvm(ptr noundef %29, i64 noundef %add.i.i.i74) #13
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit: ; preds = %if.then.i.i73, %if.then.i.i.i75
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %ref.tmp8) #10
  %inc = add nuw i64 %i.0110, 1
  %exitcond.not = icmp eq i64 %inc, %input_length
  br i1 %exitcond.not, label %for.cond.cleanup, label %for.body, !llvm.loop !24

lpad9.loopexit:                                   ; preds = %if.else.i.i.i.i
  %lpad.loopexit98 = landingpad { ptr, i32 }
          catch ptr null
  br label %lpad9

lpad9.loopexit.split-lp:                          ; preds = %if.then.i.i.i.i69
  %lpad.loopexit.split-lp99 = landingpad { ptr, i32 }
          catch ptr null
  br label %lpad9

lpad9:                                            ; preds = %lpad9.loopexit.split-lp, %lpad9.loopexit
  %lpad.phi100 = phi { ptr, i32 } [ %lpad.loopexit98, %lpad9.loopexit ], [ %lpad.loopexit.split-lp99, %lpad9.loopexit.split-lp ]
  %32 = load ptr, ptr %ref.tmp8, align 8, !tbaa !14
  %cmp.i.i.i77 = icmp eq ptr %32, %1
  br i1 %cmp.i.i.i77, label %if.then.i.i.i80, label %if.then.i.i78

if.then.i.i.i80:                                  ; preds = %lpad9
  %33 = load i64, ptr %_M_string_length.i.i.i.i62, align 8, !tbaa !11
  %cmp3.i.i.i82 = icmp ult i64 %33, 16
  call void @llvm.assume(i1 %cmp3.i.i.i82)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit83

if.then.i.i78:                                    ; preds = %lpad9
  %34 = load i64, ptr %1, align 8, !tbaa !10
  %add.i.i.i79 = add i64 %34, 1
  call void @_ZdlPvm(ptr noundef %32, i64 noundef %add.i.i.i79) #13
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit83

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit83: ; preds = %if.then.i.i78, %if.then.i.i.i80
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %ref.tmp8) #10
  br label %ehcleanup17

invoke.cont15:                                    ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit
  %35 = load ptr, ptr %result, align 8, !tbaa !14
  %cmp.i.i.i84 = icmp eq ptr %35, %0
  br i1 %cmp.i.i.i84, label %if.then.i.i.i87, label %if.then.i.i85

if.then.i.i.i87:                                  ; preds = %invoke.cont15
  %36 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %cmp3.i.i.i89 = icmp ult i64 %36, 16
  call void @llvm.assume(i1 %cmp3.i.i.i89)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit90

if.then.i.i85:                                    ; preds = %invoke.cont15
  %37 = load i64, ptr %0, align 8, !tbaa !10
  %add.i.i.i86 = add i64 %37, 1
  call void @_ZdlPvm(ptr noundef %35, i64 noundef %add.i.i.i86) #13
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit90

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit90: ; preds = %if.then.i.i85, %if.then.i.i.i87
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %result) #10
  br label %return

lpad12:                                           ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEPKc.exit, %if.else.i.i.i, %if.then.i.i.i32
  %38 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup17

ehcleanup17:                                      ; preds = %lpad12, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit83, %lpad5.loopexit.split-lp, %lpad5.loopexit
  %.pn.pn = phi { ptr, i32 } [ %38, %lpad12 ], [ %lpad.phi100, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit83 ], [ %lpad.loopexit, %lpad5.loopexit ], [ %lpad.loopexit.split-lp, %lpad5.loopexit.split-lp ]
  %39 = load ptr, ptr %result, align 8, !tbaa !14
  %cmp.i.i.i91 = icmp eq ptr %39, %0
  br i1 %cmp.i.i.i91, label %if.then.i.i.i94, label %if.then.i.i92

if.then.i.i.i94:                                  ; preds = %ehcleanup17
  %40 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !11
  %cmp3.i.i.i96 = icmp ult i64 %40, 16
  call void @llvm.assume(i1 %cmp3.i.i.i96)
  br label %ehcleanup18

if.then.i.i92:                                    ; preds = %ehcleanup17
  %41 = load i64, ptr %0, align 8, !tbaa !10
  %add.i.i.i93 = add i64 %41, 1
  call void @_ZdlPvm(ptr noundef %39, i64 noundef %add.i.i.i93) #13
  br label %ehcleanup18

ehcleanup18:                                      ; preds = %if.then.i.i92, %if.then.i.i.i94
  %exn.slot.2 = extractvalue { ptr, i32 } %.pn.pn, 0
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %result) #10
  %42 = call ptr @__cxa_begin_catch(ptr %exn.slot.2) #10
  call void @__cxa_end_catch()
  br label %return

return:                                           ; preds = %ehcleanup18, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit90, %entry
  %retval.0 = phi ptr [ null, %ehcleanup18 ], [ %call16, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit90 ], [ null, %entry ]
  ret ptr %retval.0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

declare i32 @__gxx_personality_v0(...)

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

declare noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32)) local_unnamed_addr #2

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @__cxa_end_catch() local_unnamed_addr

; Function Attrs: cold noreturn
declare void @_ZSt20__throw_length_errorPKc(ptr noundef) local_unnamed_addr #3

; Function Attrs: noinline noreturn nounwind uwtable
declare hidden void @__clang_call_terminate(ptr noundef) local_unnamed_addr #4

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nobuiltin nounwind
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #6

; Function Attrs: mustprogress uwtable
declare void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32), i64 noundef, i64 noundef, ptr noundef, i64 noundef) local_unnamed_addr #0 align 2

; Function Attrs: mustprogress uwtable
declare void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm(ptr noundef nonnull align 8 dereferenceable(32), i64 noundef) local_unnamed_addr #0 align 2

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write)
declare void @llvm.assume(i1 noundef) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.abs.i32(i32, i1 immarg) #8

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare void @llvm.experimental.noalias.scope.decl(metadata) #9

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { cold noreturn "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { noinline noreturn nounwind uwtable "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }
attributes #8 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #9 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
attributes #10 = { nounwind }
attributes #11 = { cold noreturn }
attributes #12 = { noreturn nounwind }
attributes #13 = { builtin nounwind }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!5, !6, i64 0}
!5 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE12_Alloc_hiderE", !6, i64 0}
!6 = !{!"p1 omnipotent char", !7, i64 0}
!7 = !{!"any pointer", !8, i64 0}
!8 = !{!"omnipotent char", !9, i64 0}
!9 = !{!"Simple C++ TBAA"}
!10 = !{!8, !8, i64 0}
!11 = !{!12, !13, i64 8}
!12 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE", !5, i64 0, !13, i64 8, !8, i64 16}
!13 = !{!"long", !8, i64 0}
!14 = !{!12, !6, i64 0}
!15 = !{!16, !16, i64 0}
!16 = !{!"int", !8, i64 0}
!17 = !{!18}
!18 = distinct !{!18, !19, !"_ZNSt7__cxx119to_stringEi: %agg.result"}
!19 = distinct !{!19, !"_ZNSt7__cxx119to_stringEi"}
!20 = distinct !{!20, !21, !22}
!21 = !{!"llvm.loop.mustprogress"}
!22 = !{!"llvm.loop.unroll.disable"}
!23 = distinct !{!23, !21, !22}
!24 = distinct !{!24, !21, !22}
