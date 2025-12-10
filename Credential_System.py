"""
University Credential Validation System
Uses Pandas for efficient data management and analysis
Author: Keshavraj
Date: 2024
"""

import pandas as pd
import numpy as np
import time
from collections import deque
from datetime import datetime
import os
import sys

# ==================== CREDENTIAL CLASS ====================
class Credential:
    """Represents a student's credential information"""
    
    def __init__(self, student_id, name, university, degree, cgpa, graduation_year):
        self.student_id = student_id
        self.name = name
        self.university = university
        self.degree = degree
        self.cgpa = cgpa
        self.graduation_year = graduation_year
        self.enrollment_date = datetime.now().strftime('%Y-%m-%d')
        self.verified = False
    
    def to_dict(self):
        """Convert credential to dictionary for DataFrame"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'university': self.university,
            'degree': self.degree,
            'cgpa': self.cgpa,
            'graduation_year': self.graduation_year,
            'enrollment_date': self.enrollment_date
        }

# ==================== UNIVERSITY CLASS ====================
class University:
    """
    Represents a university in the validation network
    Uses Pandas DataFrame for efficient student record management
    """
    
    def __init__(self, name, csv_file=None):
        self.name = name
        self.csv_file = csv_file or f"data/{name.replace(' ', '_')}_students.csv"
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Load existing data or create new DataFrame
        if os.path.exists(self.csv_file):
            self.students_df = pd.read_csv(self.csv_file)
            print(f"✓ Loaded {len(self.students_df)} students from {self.name}")
        else:
            self.students_df = pd.DataFrame(columns=[
                'student_id', 'name', 'university', 'degree', 
                'cgpa', 'graduation_year', 'enrollment_date'
            ])
            print(f"✓ Created new database for {self.name}")
        
        # Set student_id as index for O(1) lookup
        if not self.students_df.empty:
            self.students_df.set_index('student_id', inplace=True, drop=False)
    
    def add_student(self, student_id, name, degree, cgpa, graduation_year):
        """Add a single student to the database"""
        try:
            new_student = pd.DataFrame([{
                'student_id': student_id,
                'name': name,
                'university': self.name,
                'degree': degree,
                'cgpa': float(cgpa),
                'graduation_year': int(graduation_year),
                'enrollment_date': datetime.now().strftime('%Y-%m-%d')
            }])
            
            new_student.set_index('student_id', inplace=True, drop=False)
            self.students_df = pd.concat([self.students_df, new_student])
            print(f"  ✓ Added: {name} ({student_id})")
            return True
        except Exception as e:
            print(f"  ✗ Error adding {name}: {e}")
            return False
    
    def add_students_bulk(self, students_list):
        """
        Bulk add multiple students - much more efficient than individual adds
        students_list: List of dictionaries with student info
        """
        try:
            new_df = pd.DataFrame(students_list)
            new_df['university'] = self.name
            new_df['enrollment_date'] = datetime.now().strftime('%Y-%m-%d')
            new_df['cgpa'] = new_df['cgpa'].astype(float)
            new_df['graduation_year'] = new_df['graduation_year'].astype(int)
            new_df.set_index('student_id', inplace=True, drop=False)
            
            self.students_df = pd.concat([self.students_df, new_df])
            print(f"  ✓ Bulk added {len(students_list)} students to {self.name}")
            return True
        except Exception as e:
            print(f"  ✗ Bulk add error: {e}")
            return False
    
    def verify_student(self, student_id):
        """
        Verify if student exists - O(1) lookup using indexed DataFrame
        Returns: Dictionary with student info or None
        """
        try:
            if student_id in self.students_df.index:
                student_data = self.students_df.loc[student_id]
                return {
                    'student_id': student_data['student_id'],
                    'name': student_data['name'],
                    'university': student_data['university'],
                    'degree': student_data['degree'],
                    'cgpa': student_data['cgpa'],
                    'graduation_year': int(student_data['graduation_year']),
                    'enrollment_date': student_data['enrollment_date']
                }
            return None
        except Exception as e:
            print(f"  ✗ Verification error: {e}")
            return None
    
    def search_by_name(self, name, exact_match=False):
        """
        Search students by name
        exact_match: If True, requires exact name match; else partial match
        """
        if exact_match:
            result = self.students_df[self.students_df['name'] == name]
        else:
            result = self.students_df[
                self.students_df['name'].str.contains(name, case=False, na=False)
            ]
        return result
    
    def search_by_degree(self, degree):
        """Search students by degree program"""
        result = self.students_df[
            self.students_df['degree'].str.contains(degree, case=False, na=False)
        ]
        return result
    
    def get_students_by_cgpa_range(self, min_cgpa, max_cgpa):
        """Get students within a CGPA range"""
        result = self.students_df[
            (self.students_df['cgpa'] >= min_cgpa) & 
            (self.students_df['cgpa'] <= max_cgpa)
        ]
        return result
    
    def get_top_students(self, n=5):
        """Get top N students by CGPA"""
        return self.students_df.nlargest(n, 'cgpa')
    
    def get_recent_graduates(self, year=2024):
        """Get students who graduated in or after specified year"""
        return self.students_df[self.students_df['graduation_year'] >= year]
    
    def get_statistics(self):
        """
        Calculate comprehensive statistics using Pandas aggregation
        Returns: Dictionary with various statistics
        """
        if self.students_df.empty:
            return {
                'total_students': 0,
                'average_cgpa': 0,
                'median_cgpa': 0,
                'highest_cgpa': 0,
                'lowest_cgpa': 0,
                'degrees_offered': 0,
                'recent_graduates': 0
            }
        
        stats = {
            'total_students': len(self.students_df),
            'average_cgpa': round(self.students_df['cgpa'].mean(), 2),
            'median_cgpa': round(self.students_df['cgpa'].median(), 2),
            'highest_cgpa': round(self.students_df['cgpa'].max(), 2),
            'lowest_cgpa': round(self.students_df['cgpa'].min(), 2),
            'std_dev_cgpa': round(self.students_df['cgpa'].std(), 2),
            'degrees_offered': self.students_df['degree'].nunique(),
            'recent_graduates': len(self.students_df[
                self.students_df['graduation_year'] >= 2024
            ])
        }
        return stats
    
    def get_degree_distribution(self):
        """Get distribution of students across degree programs"""
        return self.students_df['degree'].value_counts()
    
    def get_graduation_year_distribution(self):
        """Get distribution of students by graduation year"""
        return self.students_df['graduation_year'].value_counts().sort_index()
    
    def save_to_csv(self):
        """Save DataFrame to CSV file"""
        try:
            # Reset index before saving to preserve student_id as column
            df_to_save = self.students_df.reset_index(drop=True)
            df_to_save.to_csv(self.csv_file, index=False)
            print(f"✓ Saved {self.name} data to {self.csv_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving {self.name}: {e}")
            return False
    
    def export_to_excel(self, filename=None):
        """Export university data to Excel with formatting"""
        try:
            excel_file = filename or f"reports/{self.name.replace(' ', '_')}_report.xlsx"
            os.makedirs('reports', exist_ok=True)
            
            df_to_export = self.students_df.reset_index(drop=True)
            df_to_export.to_excel(excel_file, index=False, sheet_name=self.name)
            print(f"✓ Exported {self.name} to {excel_file}")
            return True
        except Exception as e:
            print(f"✗ Export error: {e}")
            return False

# ==================== VALIDATION SYSTEM ====================
class ValidationSystem:
    """
    Central validation system that connects all universities
    Manages validation requests and maintains processing history
    """
    
    def __init__(self):
        self.universities = []
        self.validation_queue = deque()
        self.total_requests = 0
        self.successful_validations = 0
        
        # Create validation history DataFrame
        self.validation_history = pd.DataFrame(columns=[
            'request_id', 'timestamp', 'student_id', 'status', 
            'university', 'processing_time', 'requester'
        ])
        
        print("="*70)
        print("UNIVERSITY CREDENTIAL VALIDATION SYSTEM - INITIALIZED")
        print("="*70)
    
    def register_university(self, university):
        """Register a university in the validation network"""
        self.universities.append(university)
        print(f"🎓 Registered: {university.name} ({len(university.students_df)} students)")
    
    def request_validation(self, student_id, requester="System"):
        """
        Add a validation request to the queue
        student_id: Student ID to verify
        requester: Organization requesting validation (e.g., "Google", "MIT")
        """
        self.validation_queue.append((student_id, requester))
        self.total_requests += 1
        print(f"📋 Queued validation request for: {student_id} (from {requester})")
    
    def request_validations_bulk(self, student_ids, requester="System"):
        """Bulk add multiple validation requests"""
        for student_id in student_ids:
            self.validation_queue.append((student_id, requester))
            self.total_requests += 1
        print(f"📋 Queued {len(student_ids)} validation requests from {requester}")
    
    def process_validations(self):
        """
        Process all pending validation requests
        Uses queue (FIFO) for fair processing
        """
        if not self.validation_queue:
            print("⚠️  No pending validation requests")
            return
        
        print("\n" + "="*70)
        print("PROCESSING VALIDATION REQUESTS")
        print("="*70)
        
        overall_start = time.time()
        requests_to_process = len(self.validation_queue)
        
        while self.validation_queue:
            student_id, requester = self.validation_queue.popleft()
            request_start = time.time()
            
            found = False
            found_university = None
            credential = None
            
            # Search across all universities
            for university in self.universities:
                credential = university.verify_student(student_id)
                if credential:
                    found = True
                    found_university = university.name
                    self.successful_validations += 1
                    break
            
            request_time = time.time() - request_start
            
            # Display result
            if found:
                self._display_credential(credential, request_time)
            else:
                print(f"\n✗ NOT FOUND: Student ID '{student_id}' not in network")
                print(f"  Requested by: {requester}")
                print(f"  Processing time: {request_time:.4f} seconds")
            
            # Log to validation history
            new_log = pd.DataFrame([{
                'request_id': self.total_requests - len(self.validation_queue),
                'timestamp': datetime.now(),
                'student_id': student_id,
                'status': 'Success' if found else 'Not Found',
                'university': found_university if found else 'N/A',
                'processing_time': request_time,
                'requester': requester
            }])
            
            self.validation_history = pd.concat(
                [self.validation_history, new_log], 
                ignore_index=True
            )
        
        overall_time = time.time() - overall_start
        
        # Summary
        print("\n" + "="*70)
        print("VALIDATION BATCH COMPLETE")
        print("="*70)
        print(f"📊 Requests Processed: {requests_to_process}")
        print(f"✓  Successful: {self.successful_validations} "
              f"({self.successful_validations/self.total_requests*100:.1f}%)")
        print(f"✗  Not Found: {self.total_requests - self.successful_validations}")
        print(f"⏱️  Total Time: {overall_time:.4f} seconds")
        print(f"⚡ Average Time per Request: {overall_time/requests_to_process:.4f} seconds")
        print(f"🚀 Throughput: {requests_to_process/overall_time:.1f} requests/second")
    
    def _display_credential(self, credential, processing_time):
        """Display verified credential information"""
        print(f"\n{'='*70}")
        print(f"✅ CREDENTIAL VERIFIED")
        print(f"{'='*70}")
        print(f"  Student ID:       {credential['student_id']}")
        print(f"  Name:             {credential['name']}")
        print(f"  University:       {credential['university']}")
        print(f"  Degree:           {credential['degree']}")
        print(f"  CGPA:             {credential['cgpa']:.2f}")
        print(f"  Graduation Year:  {credential['graduation_year']}")
        print(f"  Enrolled:         {credential['enrollment_date']}")
        print(f"  Processing Time:  {processing_time:.4f} seconds")
    
    def search_student_by_name(self, name):
        """Search for student by name across all universities"""
        print(f"\n🔍 Searching for: '{name}' across all universities...")
        
        all_results = []
        for university in self.universities:
            results = university.search_by_name(name)
            if not results.empty:
                all_results.append(results)
        
        if all_results:
            combined_results = pd.concat(all_results, ignore_index=True)
            print(f"\n✓ Found {len(combined_results)} match(es):\n")
            print(combined_results[['name', 'student_id', 'university', 'degree', 'cgpa']].to_string(index=False))
            return combined_results
        else:
            print(f"✗ No matches found for '{name}'")
            return pd.DataFrame()
    
    def get_analytics(self):
        """Display comprehensive system analytics"""
        print("\n" + "="*70)
        print("SYSTEM ANALYTICS & STATISTICS")
        print("="*70)
        
        # Overall system statistics
        print(f"\n📊 OVERALL SYSTEM STATISTICS:")
        print(f"   {'─'*66}")
        print(f"   Universities in Network:     {len(self.universities)}")
        
        total_students = sum(len(uni.students_df) for uni in self.universities)
        print(f"   Total Students in Database:  {total_students:,}")
        print(f"   Total Validation Requests:   {self.total_requests}")
        print(f"   Successful Validations:      {self.successful_validations}")
        
        if self.total_requests > 0:
            success_rate = (self.successful_validations / self.total_requests) * 100
            print(f"   Success Rate:                {success_rate:.2f}%")
        
        # Processing time statistics
        if not self.validation_history.empty:
            print(f"\n⏱️  PROCESSING TIME ANALYSIS:")
            print(f"   {'─'*66}")
            avg_time = self.validation_history['processing_time'].mean()
            median_time = self.validation_history['processing_time'].median()
            min_time = self.validation_history['processing_time'].min()
            max_time = self.validation_history['processing_time'].max()
            
            print(f"   Average Time:     {avg_time:.4f} seconds")
            print(f"   Median Time:      {median_time:.4f} seconds")
            print(f"   Fastest Request:  {min_time:.4f} seconds")
            print(f"   Slowest Request:  {max_time:.4f} seconds")
            
            # Validation distribution by university
            print(f"\n🎓 VALIDATIONS BY UNIVERSITY:")
            print(f"   {'─'*66}")
            success_by_uni = self.validation_history[
                self.validation_history['status'] == 'Success'
            ]['university'].value_counts()
            
            for uni, count in success_by_uni.items():
                print(f"   {uni:30s} {count:3d} validations")
            
            # Requester distribution
            print(f"\n🏢 REQUESTS BY ORGANIZATION:")
            print(f"   {'─'*66}")
            requester_dist = self.validation_history['requester'].value_counts()
            for requester, count in requester_dist.items():
                print(f"   {requester:30s} {count:3d} requests")
        
        # University-wise statistics
        print(f"\n📚 UNIVERSITY-WISE DETAILED STATISTICS:")
        print(f"   {'='*66}")
        
        for uni in self.universities:
            stats = uni.get_statistics()
            print(f"\n   {uni.name}")
            print(f"   {'─'*66}")
            print(f"   Total Students:           {stats['total_students']:,}")
            print(f"   Average CGPA:             {stats['average_cgpa']:.2f}")
            print(f"   Median CGPA:              {stats['median_cgpa']:.2f}")
            print(f"   Highest CGPA:             {stats['highest_cgpa']:.2f}")
            print(f"   Lowest CGPA:              {stats['lowest_cgpa']:.2f}")
            print(f"   Std Deviation:            {stats['std_dev_cgpa']:.2f}")
            print(f"   Degrees Offered:          {stats['degrees_offered']}")
            print(f"   Recent Graduates (2024+): {stats['recent_graduates']}")
            
            # Top 3 students
            if not uni.students_df.empty:
                print(f"\n   Top 3 Students:")
                top_3 = uni.get_top_students(3)
                for idx, student in top_3.iterrows():
                    print(f"     • {student['name']:25s} CGPA: {student['cgpa']:.2f}")
    
    def export_comprehensive_report(self, filename='comprehensive_report.xlsx'):
        """Export comprehensive system report to Excel"""
        try:
            os.makedirs('reports', exist_ok=True)
            filepath = f"reports/{filename}"
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Sheet 1: Validation History
                self.validation_history.to_excel(
                    writer, sheet_name='Validation History', index=False
                )
                
                # Sheet 2: Combined Student Database
                all_students_list = []
                for uni in self.universities:
                    if not uni.students_df.empty:
                        df_copy = uni.students_df.reset_index(drop=True)
                        all_students_list.append(df_copy)
                
                if all_students_list:
                    all_students = pd.concat(all_students_list, ignore_index=True)
                    all_students.to_excel(
                        writer, sheet_name='All Students', index=False
                    )
                
                # Sheet 3: Statistics Summary
                stats_data = []
                for uni in self.universities:
                    stats = uni.get_statistics()
                    stats['university'] = uni.name
                    stats_data.append(stats)
                
                if stats_data:
                    stats_df = pd.DataFrame(stats_data)
                    stats_df = stats_df[['university', 'total_students', 'average_cgpa', 
                                        'median_cgpa', 'highest_cgpa', 'degrees_offered', 
                                        'recent_graduates']]
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)
                
                # Sheet 4: System Summary
                system_summary = pd.DataFrame([{
                    'Metric': 'Total Universities',
                    'Value': len(self.universities)
                }, {
                    'Metric': 'Total Students',
                    'Value': sum(len(uni.students_df) for uni in self.universities)
                }, {
                    'Metric': 'Total Validation Requests',
                    'Value': self.total_requests
                }, {
                    'Metric': 'Successful Validations',
                    'Value': self.successful_validations
                }, {
                    'Metric': 'Success Rate (%)',
                    'Value': round((self.successful_validations/self.total_requests*100) 
                                  if self.total_requests > 0 else 0, 2)
                }])
                system_summary.to_excel(writer, sheet_name='System Summary', index=False)
            
            print(f"\n✅ Comprehensive report exported to: {filepath}")
            return True
        except Exception as e:
            print(f"\n❌ Error exporting report: {e}")
            return False
    
    def save_all_data(self):
        """Save all university data to CSV files"""
        print("\n💾 Saving all university data...")
        for uni in self.universities:
            uni.save_to_csv()
        print("✅ All data saved successfully")

# ==================== MAIN DEMO FUNCTION ====================
def main():
    """
    Main demonstration function
    Shows all features of the credential validation system
    """
    print("\n" + "="*70)
    print("UNIVERSITY CREDENTIAL VALIDATION SYSTEM")
    print("Powered by Pandas for Efficient Data Management")
    print("="*70)
    
    # Initialize system
    system = ValidationSystem()
    
    # Create universities
    print("\n📚 INITIALIZING UNIVERSITIES...")
    print("─"*70)
    
    mit = University("MIT")
    stanford = University("Stanford University")
    berkeley = University("UC Berkeley")
    harvard = University("Harvard University")
    
    # Register universities
    system.register_university(mit)
    system.register_university(stanford)
    system.register_university(berkeley)
    system.register_university(harvard)
    
    # Add students - Individual additions
    print("\n👨‍🎓 ADDING STUDENTS (Individual)...")
    print("─"*70)
    
    mit.add_student("MIT001", "Alice Johnson", "Computer Science", 3.85, 2023)
    mit.add_student("MIT002", "Bob Smith", "Electrical Engineering", 3.62, 2024)
    mit.add_student("MIT003", "Carol White", "Mechanical Engineering", 3.91, 2023)
    
    # Bulk add students (more efficient!)
    print("\n👥 BULK ADDING STUDENTS...")
    print("─"*70)
    
    stanford_students = [
        {'student_id': 'STAN001', 'name': 'Charlie Brown', 'degree': 'Data Science', 'cgpa': 3.95, 'graduation_year': 2023},
        {'student_id': 'STAN002', 'name': 'Eva Green', 'degree': 'Machine Learning', 'cgpa': 3.78, 'graduation_year': 2024},
        {'student_id': 'STAN003', 'name': 'Frank Miller', 'degree': 'Artificial Intelligence', 'cgpa': 3.88, 'graduation_year': 2023},
        {'student_id': 'STAN004', 'name': 'Helen Troy', 'degree': 'Data Science', 'cgpa': 3.72, 'graduation_year': 2024},
    ]
    stanford.add_students_bulk(stanford_students)
    
    berkeley_students = [
        {'student_id': 'BERK001', 'name': 'Diana Prince', 'degree': 'Cybersecurity', 'cgpa': 3.96, 'graduation_year': 2024},
        {'student_id': 'BERK002', 'name': 'Grace Hopper', 'degree': 'Software Engineering', 'cgpa': 4.00, 'graduation_year': 2023},
        {'student_id': 'BERK003', 'name': 'Isaac Newton', 'degree': 'Computer Science', 'cgpa': 3.89, 'graduation_year': 2024},
    ]
    berkeley.add_students_bulk(berkeley_students)
    
    harvard_students = [
        {'student_id': 'HARV001', 'name': 'Jane Doe', 'degree': 'Computer Science', 'cgpa': 3.81, 'graduation_year': 2023},
        {'student_id': 'HARV002', 'name': 'John Smith', 'degree': 'Information Technology', 'cgpa': 3.68, 'graduation_year': 2024},
        {'student_id': 'HARV003', 'name': 'Maria Garcia', 'degree': 'Data Analytics', 'cgpa': 3.92, 'graduation_year': 2024},
    ]
    harvard.add_students_bulk(harvard_students)
    
    # Demonstrate Pandas features
    print("\n🔍 PANDAS FEATURE DEMONSTRATION...")
    print("─"*70)
    
    print("\n1. Top 3 Students at Stanford (sorted by CGPA):")
    top_students = stanford.get_top_students(3)
    print(top_students[['name', 'degree', 'cgpa']].to_string(index=False))
    
    print("\n2. Search for students named 'Smith' across all universities:")
    system.search_student_by_name("Smith")
    
    print("\n3. Berkeley students with CGPA > 3.9:")
    high_performers = berkeley.get_students_by_cgpa_range(3.9, 4.0)
    print(high_performers[['name', 'degree', 'cgpa']].to_string(index=False))
    
    # Validation requests simulation
    print("\n📋 SUBMITTING VALIDATION REQUESTS...")
    print("─"*70)
    
    # Single requests
    system.request_validation("MIT001", "Google Inc.")
    system.request_validation("STAN002", "Microsoft")
    system.request_validation("BERK001", "Amazon")
    system.request_validation("MIT999", "Meta")  # This won't be found
    system.request_validation("HARV001", "Apple")
    
    # Bulk requests
    system.request_validations_bulk(
        ["STAN001", "MIT002", "BERK002", "HARV003"], 
        "Tesla"
    )
    
    # Process all validations
    print("\n")
    system.process_validations()
    
    # Display analytics
    system.get_analytics()
    
    # Save all data
    system.save_all_data()
    
    # Export comprehensive report
    system.export_comprehensive_report()
    
    # Final summary
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    print("\n📁 Generated Files:")
    print("   • CSV files in 'data/' directory (student databases)")
    print("   • Excel report in 'reports/' directory (comprehensive report)")
    print("\n💡 Tips:")
    print("   • Run this program again - data will be loaded from CSV files")
    print("   • Check the Excel report for detailed analytics")
    print("   • Modify student data and re-run to see persistence")
    print("\n" + "="*70)

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)