import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { 
  Leaf, 
  Users, 
  Truck, 
  Shield, 
  TrendingUp, 
  Globe 
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-20">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Welcome to <span className="text-primary-600">AgriLink</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Connect local farmers to aggregators, exporters, and end-users. 
          Reduce crop spoilage, improve farmer incomes, and get fresh produce at competitive prices.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/auth/register">
            <Button size="lg">Get Started</Button>
          </Link>
          <Link href="/listings">
            <Button variant="outline" size="lg">Browse Listings</Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section>
        <h2 className="text-3xl font-bold text-center mb-12">Why Choose AgriLink?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Card className="text-center p-6">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Leaf className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Direct Farm-to-Buyer</h3>
            <p className="text-gray-600">
              Eliminate middlemen and connect directly with verified farmers for better prices.
            </p>
          </Card>

          <Card className="text-center p-6">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Secure Escrow System</h3>
            <p className="text-gray-600">
              Safe payment processing with escrow protection for both buyers and sellers.
            </p>
          </Card>

          <Card className="text-center p-6">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Truck className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Logistics Support</h3>
            <p className="text-gray-600">
              Integrated logistics and cold-chain transport for fresh produce delivery.
            </p>
          </Card>
        </div>
      </section>

      {/* How It Works */}
      <section>
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              1
            </div>
            <h3 className="text-lg font-semibold mb-2">Register & Verify</h3>
            <p className="text-gray-600">Create account and complete KYC verification</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              2
            </div>
            <h3 className="text-lg font-semibold mb-2">List or Browse</h3>
            <p className="text-gray-600">Farmers list produce, buyers browse offerings</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              3
            </div>
            <h3 className="text-lg font-semibold mb-2">Make Offers</h3>
            <p className="text-gray-600">Buyers make offers, farmers accept best ones</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              4
            </div>
            <h3 className="text-lg font-semibold mb-2">Complete Transaction</h3>
            <p className="text-gray-600">Escrow funding, delivery, and payment release</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center py-16 bg-primary-50 rounded-2xl">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Transform Agriculture?
        </h2>
        <p className="text-lg text-gray-600 mb-8">
          Join thousands of farmers and buyers already using AgriLink
        </p>
        <Link href="/auth/register">
          <Button size="lg">Start Your Journey Today</Button>
        </Link>
      </section>
    </div>
  )
}
